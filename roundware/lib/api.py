from __future__ import unicode_literals
from rest_framework.exceptions import ParseError
from roundware.rw import models
from roundware.lib import dbus_send, discover_audiolength, convertaudio
from roundware.lib.exception import RoundException
from roundwared import gpsmixer
from roundwared import icecast2
from django.conf import settings
from django.db.models import Count, Avg
from django.http import Http404
import datetime
import json
import os
import subprocess
import sys
import time
import logging

logger = logging.getLogger(__name__)


def t(msg, field, language):
    """
    Locates the translation for the msg in the field object for the provided
    session language.
    """
    # TODO: Replace with standard Django internationalization.
    try:
        msg = field.filter(language=language)[0].localized_string
    except:
        pass
    return msg


def get_project_tags(p=None, s=None):
    if s is None and p is None:
        raise RoundException("Must pass either a project or a session")
    language = models.Language.objects.filter(language_code='en')[0]
    if s is not None:
        p = s.project
        language = s.language

    m = models.MasterUI.objects.filter(project=p)
    modes = {}

    for masterui in m:
        if masterui.active:
            mappings = models.UIMapping.objects.filter(
                master_ui=masterui, active=True)
            header = t("", masterui.header_text_loc, language)

            masterD = {'name': masterui.name,
                       'header_text': header,
                       'code': masterui.tag_category.name,
                       'select': masterui.get_select_display(),
                       'order': masterui.index
                       }
            masterOptionsList = []

            default = []
            for mapping in mappings:
                loc_desc = t("", mapping.tag.loc_description, language)
                if mapping.default:
                    default.append(mapping.tag.id)
                # masterOptionsList.append(mapping.toTagDictionary())
                # def toTagDictionary(self):
                    # return
                    # {'tag_id':self.tag.id,'order':self.index,'value':self.tag.value}

                masterOptionsList.append({'tag_id': mapping.tag.id, 'order': mapping.index, 'data': mapping.tag.data,
                                          'relationships': mapping.tag.get_relationships(),
                                          'description': mapping.tag.description, 'shortcode': mapping.tag.value,
                                          'loc_description': loc_desc,
                                          'value': t("", mapping.tag.loc_msg, language)})
            masterD["options"] = masterOptionsList
            masterD["defaults"] = default
            if masterui.ui_mode not in modes:
                modes[masterui.ui_mode] = [masterD, ]
            else:
                modes[masterui.ui_mode].append(masterD)

    return modes


# @profile(stats=True)
def request_stream(request):
    session_id = request.GET.get('session_id', None)
    if session_id is None and hasattr(request, 'data'):
        session_id = request.data.get('session_id', None)
    if not session_id:
        raise RoundException("Must supply session_id.")

    log_event("request_stream", int(session_id), request.GET)

    session = models.Session.objects.select_related(
        'project').get(id=session_id)
    project = session.project

    # Get the value 'example.com' from the host 'example.com:8888'
    http_host = request.get_host().split(':')[0]

    if session.demo_stream_enabled:
        msg = t("demo_stream_message", project.demo_stream_message_loc,
                session.language)

        if project.demo_stream_url:
            url = project.demo_stream_url
        else:
            url = "http://%s:%s/demo_stream.mp3" % (http_host,
                                                    settings.ICECAST_PORT)
        return {
            'stream_url': url,
            'demo_stream_message': msg
        }

    elif is_listener_in_range_of_stream(request.GET, project):
        # TODO: audio_format.upper() should be handled when the project is saved.
        audio_format = project.audio_format.upper()
        # Make the audio stream if it doesn't exist.
        if not stream_exists(session.id, audio_format):
            command = [settings.PROJECT_ROOT + '/roundwared/rwstreamd.py',
                       '--session_id', str(session.id), '--project_id', str(project.id)]
            for p in ['latitude', 'longitude', 'audio_format']:
                if p in request.GET and request.GET[p]:
                    command.extend(['--' + p, request.GET[p].replace("\t", ",")])
            if 'audio_stream_bitrate' in request.GET:
                command.extend(
                    ['--audio_stream_bitrate', str(request.GET['audio_stream_bitrate'])])

            apache_safe_daemon_subprocess(command)
            wait_for_stream(session.id, audio_format)

        return {
            "stream_url": "http://%s:%s%s" % (http_host, settings.ICECAST_PORT,
                                              icecast2.mount_point(session.id, audio_format))
        }
    else:
        msg = t("This application is designed to be used in specific geographic"
                " locations. Apparently your phone thinks you are not at one of"
                " those locations, so you will hear a sample audio stream"
                " instead of the real deal. If you think your phone is"
                " incorrect, please restart Scapes and it will probably work."
                " Thanks for checking it out!",
                project.out_of_range_message_loc, session.language)

        return {
            'stream_url': project.out_of_range_url,
            'user_message': msg
        }


# Used by server.py many times and stream.py once!
def log_event(event_type, session_id, form=None):
    """
    event_type <string>
    session_id <integer>
    [client_time] <string using RFC822 format>
    [latitude] <float>
    [longitude] <float>
    [tags]
    [data]
    """
    s = models.Session.objects.get(id=session_id)
    if not s:
        raise RoundException("Failed to access session: %s " % session_id)
    client_time = None
    latitude = None
    longitude = None
    tags = None
    data = None
    if form:
        client_time = form.get("client_time", None)
        latitude = form.get("latitude", None)
        longitude = form.get("longitude", None)
        tags = form.get("tags", None)
        if tags is None:
            tags = form.get("tag_ids", None)
        data = form.get("data", None)

    e = models.Event(session=s,
                     event_type=event_type,
                     server_time=datetime.datetime.now(),
                     client_time=client_time,
                     latitude=latitude,
                     longitude=longitude,
                     tags=tags,
                     data=data)
    e.save()
    return e


def is_listener_in_range_of_stream(form, proj):
    # If latitude and longitude is not specified assume True.
    if not ('latitude' in form and 'longitude' in form) or not (form['latitude'] and form['longitude']):
        return True
    # Get all active speakers
    speakers = models.Speaker.objects.filter(project=proj, activeyn=True)

    for speaker in speakers:
        distance = gpsmixer.distance_in_meters(
            float(form['latitude']),
            float(form['longitude']),
            speaker.latitude,
            speaker.longitude)
        if distance < 3 * speaker.maxdistance:
            return True
    return False


def stream_exists(sessionid, audio_format):
    admin = icecast2.Admin()
    return admin.stream_exists(icecast2.mount_point(sessionid, audio_format))


def apache_safe_daemon_subprocess(command):
    logger.debug(str(command))
    env = os.environ.copy()
    env['PYTHONPATH'] = ":".join(sys.path)

    # TODO: A method to get the stdout/stderr data which doesn't deadlock
    proc = subprocess.Popen(
        command,
        close_fds=True,
        # stdout=subprocess.PIPE,
        # stderr=subprocess.PIPE,
        env=env,
    )
    # (stdout, stderr) = proc.communicate()
    # logger.debug("subprocess_stdout: " + stdout)
    # logger.debug("subprocess_stdout: " + stderr)


def wait_for_stream(sessionid, audio_format):
    """
    Loops until the give stream is present and ready to be listened to.
    """
    # Number of retries
    retries_left = 15

    logger.debug("Checking for existence of stream %s%s on %s:%s", sessionid,
                 audio_format, settings.ICECAST_HOST, settings.ICECAST_PORT)
    while not stream_exists(sessionid, audio_format):
        time.sleep(1)
        retries_left -= 1
        if retries_left < 0:
            raise RoundException("Stream timeout on creation")


def modify_stream(request, context=None):
    success = False
    msg = ""
    # api v2
    if context is not None and "pk" in context:
        form = request.data.copy()
        form["session_id"] = context["pk"]
    # api v1
    else:
        form = request.GET
    request = form_to_request(form)
    arg_hack = json.dumps(request)
    log_event("modify_stream", int(form['session_id']), form)
    logger.debug(request)

    if 'session_id' in form:
        session = models.Session.objects.select_related(
            'project').get(id=form['session_id'])
        project = session.project
        if 'language' in form:
            try:
                logger.debug("modify_stream: language: " + form['language'])
                l = models.Language.objects.filter(
                    language_code=form['language'])[0]
                session.language = l
                session.save()
            except:
                raise RoundException("language not supported")

        audio_format = project.audio_format.upper()
        if stream_exists(int(form['session_id']), audio_format):
            dbus_send.emit_stream_signal(
                int(form['session_id']), "modify_stream", arg_hack)
            success = True
        else:
            msg = "no stream available for session: " + form['session_id']
    else:
        msg = "a session_id is required for this operation"

    if success:
        return {"success": success}
    else:
        return {"success": False,
                "error": msg}


def form_to_request(form):
    request = {}
    for p in ['project_id', 'session_id', 'asset_id']:
        if p in form and form[p]:
            request[p] = map(int, form[p].split("\t"))
        else:
            request[p] = []
    request['tags'] = []
    for p in ['tags', 'tag_ids']:
        if p in form and form[p]:
            # make sure we don't have blank values from trailing commas
            p_list = [v for v in form[p].split(",") if v != ""]
            request['tags'] = map(int, p_list)

    for p in ['latitude', 'longitude']:
        if p in form and form[p]:
            request[p] = float(form[p])
        else:
            request[p] = False
    return request


def move_listener(request, context=None):
    if context is not None and "pk" in context:
        form = request.data.copy()
        form['session_id'] = context["pk"]
    else:
        form = request.GET
    try:
        request = form_to_request(form)
        arg_hack = json.dumps(request)
        log_event("move_listener", int(form['session_id']), form)
        dbus_send.emit_stream_signal(
            int(form['session_id']), "move_listener", arg_hack)
        return {"success": True}
    except Exception as e:
        return {"success": False,
                "error": "could not move listener: %s" % e}


def heartbeat(request, session_id=None):
    if session_id is None:
        session_id = request.GET['session_id']
    dbus_send.emit_stream_signal(int(session_id), "heartbeat", "")
    log_event("heartbeat", int(session_id), request.GET)
    return {"success": True}


def skip_ahead(request, session_id=None):
    if session_id is None:
        session_id = request.GET.get('session_id', None)
    if session_id is None:
        raise RoundException("a session_id is required for this operation")

    log_event("skip_ahead", int(session_id))
    if not check_for_single_audiotrack(session_id):
        raise RoundException("this operation is only valid for projects with 1 audiotrack")

    dbus_send.emit_stream_signal(int(session_id), "skip_ahead", "")
    return {"success": True}


def check_for_single_audiotrack(session_id):
    ret = False
    session = models.Session.objects.select_related(
        'project').get(id=session_id)
    tracks = models.Audiotrack.objects.filter(project=session.project)
    if tracks.count() == 1:
        ret = True
    return ret


# create_envelope
# args: (operation, session_id, [tags])
# example: http://localhost/roundware/?operation=create_envelope&session_id=1
# returns envelope_id, sharing_messsage
# example:
# {"envelope_id": 2}
# @profile(stats=True)
def create_envelope(request):
    form = request.GET
    if 'session_id' not in form:
        raise RoundException("a session_id is required for this operation")
    s = models.Session.objects.get(id=form.get('session_id'))

    env = models.Envelope(session=s)
    env.save()

    return {"envelope_id": env.id}


# add_asset_to_envelope (POST method)
# args (operation, envelope_id, session_id, file, latitude, longitude, [tagids])
# example: http://localhost/roundware/?operation=add_asset_to_envelope
# OR
# add_asset_to_envelope (GET method)
# args (operation, envelope_id, asset_id) #asset_id must point to an Asset that exists in the database
# returns success bool
# {"success": true}
# @profile(stats=True)
def add_asset_to_envelope(request, envelope_id=None):
    # get asset_id from the GET request
    asset_id = get_parameter_from_request(request, 'asset_id')
    asset = None
    # grab the Asset from the database, if an asset_id has been passed in
    if asset_id:
        try:
            asset = models.Asset.objects.get(pk=asset_id)
        except models.Asset.DoesNotExist:
            raise RoundException(
                "Invalid Asset ID Provided. No Asset exists with ID %s" % asset_id)

    if envelope_id is None:
        envelope_id = get_parameter_from_request(request, 'envelope_id', True)
    logger.debug("Found envelope_id: %s", envelope_id)

    try:
        envelope = models.Envelope.objects.select_related(
            'session').get(id=envelope_id)
    except models.Envelope.DoesNotExist:
        raise RoundException(
            "Invalid Envelope ID Provided. No Envelope exists with ID %s" % envelope_id)

    session = envelope.session

    asset = save_asset_from_request(request, session, asset=asset)

    envelope.assets.add(asset)
    envelope.save()
    logger.info("Session %s - Asset %s created for file: %s",
                session.id, asset.id, asset.file.name)

    # Refresh recordings for ALL existing streams.
    dbus_send.emit_stream_signal(0, "refresh_recordings", "")
    return {"success": True,
            "asset_id": asset.id}


def save_asset_from_request(request, session, asset=None):
    log_event("start_upload", session.id, request.GET)
    fileitem = asset.file if asset else request.FILES.get('file')
    if fileitem is None or not fileitem.name:
        raise RoundException("No file in request")

    # get mediatype from the GET request
    mediatype = get_parameter_from_request(
        request, 'mediatype') if not asset else asset.mediatype
    # also observe properly underscored version of same field
    if mediatype is None:
        mediatype = get_parameter_from_request(request, 'media_type')
    # if mediatype parameter not passed, set to 'audio'
    # this ensures backwards compatibility
    if mediatype is None:
        mediatype = "audio"

    # copy the file to a unique name (current time and date)
    logger.debug("Session %s - Processing:%s", session.id, fileitem.name)
    (filename_prefix, filename_extension) = os.path.splitext(fileitem.name)

    dest_file = time.strftime("%Y%m%d-%H%M%S-") + str(session.id)
    dest_filename = dest_file + filename_extension
    dest_filepath = os.path.join(settings.MEDIA_ROOT, dest_filename)
    count = 0
    # If the file exists add underscore and a number until it doesn't.`
    while (os.path.isfile(dest_filepath)):
        dest_filename = "%s_%d%s" % (dest_file, count, filename_extension)
        dest_filepath = os.path.join(settings.MEDIA_ROOT, dest_filename)
        count += 1

    fileout = open(dest_filepath, 'wb')
    fileout.write(fileitem.file.read())
    fileout.close()

    # Delete the uploaded original after the copy has been made.
    if asset:
        asset.file.delete()
        asset.file.name = dest_filename
        asset.filename = dest_filename
        asset.save()
    # Make sure everything is in wav form only if media type is audio.
    if mediatype == "audio":
        newfilename = convertaudio.convert_uploaded_file(dest_filename)
    else:
        newfilename = dest_filename
    if not newfilename:
        raise RoundException("File not converted successfully: " + newfilename)

    # if the request comes from the django admin interface
    # update the Asset with the right information
    if asset:
        asset.session = session
        asset.filename = newfilename
    # create the new asset if request comes in from a source other
    # than the django admin interface
    else:
        # get location data from request
        latitude = get_parameter_from_request(request, 'latitude')
        longitude = get_parameter_from_request(request, 'longitude')
        # if no location data in request, default to project latitude
        # and longitude
        if not latitude:
            latitude = session.project.latitude
        if not longitude:
            longitude = session.project.longitude
        tagset = []
        tags = get_parameter_from_request(request, 'tags')
        if tags is None:
            tags = get_parameter_from_request(request, 'tag_ids')
        if tags is not None:
            ids = tags.rstrip(',').split(',')
            try:
                tagset = models.Tag.objects.filter(id__in=ids)
            except:
                raise RoundException("Could not decode tag list")

        # get optional submitted parameter from request (Y, N or blank
        # string are only acceptable values)
        submitted = get_parameter_from_request(request, 'submitted')
        # set submitted variable to proper boolean value if it is
        # passed as parameter
        if submitted == "N":
            submitted = False
        elif submitted == "Y":
            submitted = True
        # if blank string or not included as parameter, check if in range of project and if so
        # set asset.submitted based on project.auto_submit boolean
        # value
        elif submitted is None or len(submitted) == 0:
            submitted = False
            if is_listener_in_range_of_stream(request.GET, session.project):
                submitted = session.project.auto_submit

        # save description if provided, null is not allowed
        description = get_parameter_from_request(request, 'description')
        if description is None:
            description = ""

        asset = models.Asset(latitude=latitude,
                             longitude=longitude,
                             filename=newfilename,
                             session=session,
                             submitted=submitted,
                             mediatype=mediatype,
                             description=description,
                             volume=1.0,
                             language=session.language,
                             project=session.project)
        asset.file.name = dest_filename
        asset.save()
        for tag in tagset:
            asset.tags.add(tag)

    # get the audiolength of the file only if mediatype is audio and
    # update the Asset
    if mediatype == "audio":
        discover_audiolength.discover_and_set_audiolength(
            asset, newfilename)
        asset.save()

    return asset


def get_parameter_from_request(request, name, required=False):
    ret = None
    try:
        ret = request.POST[name]
    except (KeyError, AttributeError):
        try:
            ret = request.GET[name]
        except (KeyError, AttributeError):
            try:
                ret = request.data[name]
            except (KeyError, AttributeError):
                if required:
                    raise RoundException(name + " is required for this operation")
    return ret


def get_current_streaming_asset(request, session_id=None):
    if session_id is None:
        session_id = request.GET.get('session_id', None)
    if session_id is None:
        raise RoundException("a session_id is required for this operation")
    if check_for_single_audiotrack(session_id) is not True:
        raise RoundException("this operation is only valid for projects with 1 audiotrack")
    else:
        l = _get_current_streaming_asset(session_id)
    if l:
        return {"asset_id": l.asset.id,
                "start_time": l.starttime.isoformat(),
                "duration_in_stream": l.duration / 1000000,
                "current_server_time": datetime.datetime.now().isoformat()}
    else:
        raise RoundException("no asset found")


def _get_current_streaming_asset(session_id):
    try:
        l = models.ListeningHistoryItem.objects.filter(
            session=session_id).order_by('-starttime')[0]
        return l
    except IndexError:
        return None


def vote_asset(request, asset_id=None):
    if hasattr(request, 'data'):
        form = request.data
    else:
        form = request.GET

    if 'session_id' not in form:
        raise RoundException("a session_id is required for this operation")
    if 'asset_id' not in form and asset_id is None:
        raise RoundException("an asset_id is required for this operation")
    if 'vote_type' not in form:
        raise RoundException("a vote_type is required for this operation")
    if not check_for_single_audiotrack(form.get('session_id')):
        raise RoundException(
            "this operation is only valid for projects with 1 audiotrack")

    try:
        log_event("vote_asset", int(form.get('session_id')), form)
        session = models.Session.objects.get(id=int(form.get('session_id')))
    except:
        raise RoundException("Session not found.")
    try:
        if asset_id is None:
            asset_id = int(form.get('asset_id'))
        asset = models.Asset.objects.get(id=asset_id)
    except:
        raise RoundException("Asset not found.")

    # try to find existing vote for this session and asset
    existing = models.Vote.objects.filter(session=session, asset=asset, type=form.get('vote_type'))
    if len(existing) > 0:
        # if value not included - remove old vote (toggle)
        if "value" not in form:
            existing.delete()
        # if value included - update value and resave
        else:
            existing.update(value=form.get('value'))
        v = existing.first()
    else:
        if 'value' not in form:
            v = models.Vote(
                asset=asset, session=session, type=form.get('vote_type'))
        else:
            v = models.Vote(asset=asset, session=session, value=int(
                form.get('value')), type=form.get('vote_type'))
        v.save()
    return {"success": True, "vote": v}


###################################
# WARNING
###################################

# APIv2 ONLY BELOW THIS POINT
# the functions below have not been tested, and likely do not work
# with the request style of APIv1

###################################
# WARNING
###################################


def vote_count_by_asset(asset_id):
    """
    Provides a count of votes, by vote type, for a given asset
    """
    counts = models.Vote.objects.all() \
                                .filter(asset_id=asset_id) \
                                .values('type') \
                                .annotate(total=Count('type')).order_by('total')
    avg = models.Vote.objects.all().filter(asset_id=asset_id, type="rate").aggregate(Avg('value'))
    if avg["value__avg"] is not None:
        for count in counts:
            if count["type"] == "rate":
                count["avg"] = avg["value__avg"]
    return counts
