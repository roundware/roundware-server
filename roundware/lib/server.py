# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
import time
import subprocess
import os
import sys
import logging
import json
import uuid
import datetime
import psutil
try:
    from profiling import profile
except ImportError:
    pass
from django.conf import settings
from roundware.rw import models
from roundware.lib import convertaudio
from roundware.lib import discover_audiolength
from roundware.lib import rwdbus_send
from roundware.lib.exception import RoundException
from roundwared import icecast2
from roundwared import gpsmixer

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

def check_for_single_audiotrack(session_id):
    ret = False
    session = models.Session.objects.select_related(
        'project').get(id=session_id)
    tracks = models.Audiotrack.objects.filter(project=session.project)
    if tracks.count() == 1:
        ret = True
    return ret


def get_current_streaming_asset(request):
    form = request.GET
    if 'session_id' not in form:
        raise RoundException("a session_id is required for this operation")
    if check_for_single_audiotrack(form.get('session_id')) != True:
        raise RoundException(
            "this operation is only valid for projects with 1 audiotrack")
    else:
        l = _get_current_streaming_asset(form.get('session_id'))
    if l:
        return {"asset_id": l.asset.id,
                "start_time": l.starttime.isoformat(),
                "duration_in_stream": l.duration / 1000000,
                "current_server_time": datetime.datetime.now().isoformat()}
    else:
        return {"user_error_message": "no asset found"}

def _get_current_streaming_asset(session_id):
    try:
        l = models.ListeningHistoryItem.objects.filter(
            session=session_id).order_by('-starttime')[0]
        return l
    except IndexError:
        return None


def get_asset_info(request):
    form = request.GET
    if 'asset_id' not in form:
        raise RoundException("an asset_id is required for this operation")

    if not check_for_single_audiotrack(form.get('session_id')):
        raise RoundException(
            "this operation is only valid for projects with 1 audiotrack")
    else:
        a = models.Asset.objects.get(id=form.get('asset_id'))
    if a:
        return {"asset_id": a.id,
                "created": a.created.isoformat(),
                "duraton_in_ms": a.audiolength / 1000000}
    else:
        return {"user_error_message": "asset not found"}


def play_asset_in_stream(request):
    form = request.GET

    request = form_to_request(form)
    arg_hack = json.dumps(request)
    log_event("play_asset_in_stream", int(form['session_id']), form)

    if 'session_id' not in form:
        raise RoundException("a session_id is required for this operation")
    if not check_for_single_audiotrack(form.get('session_id')):
        raise RoundException(
            "this operation is only valid for projects with 1 audiotrack")
    if 'asset_id' not in form:
        raise RoundException(
            "an asset_id is required for this operation")
    rwdbus_send.emit_stream_signal(
        int(form['session_id']), "play_asset", arg_hack)
    return {"success": True}


def skip_ahead(request):
    form = request.GET
    log_event("skip_ahead", int(form['session_id']), form)

    if 'session_id' not in form:
        raise RoundException("a session_id is required for this operation")
    if not check_for_single_audiotrack(form.get('session_id')):
        raise RoundException(
            "this operation is only valid for projects with 1 audiotrack")
    rwdbus_send.emit_stream_signal(int(form['session_id']), "skip_ahead", "")
    return {"success": True}


def vote_asset(request):
    form = request.GET
    log_event("vote_asset", int(form['session_id']), form)

    if 'session_id' not in form:
        raise RoundException("a session_id is required for this operation")
    if 'asset_id' not in form:
        raise RoundException("an asset_id is required for this operation")
    if 'vote_type' not in form:
        raise RoundException("a vote_type is required for this operation")
    if not check_for_single_audiotrack(form.get('session_id')):
        raise RoundException(
            "this operation is only valid for projects with 1 audiotrack")

    try:
        session = models.Session.objects.get(id=int(form.get('session_id')))
    except:
        raise RoundException("Session not found.")
    try:
        asset = models.Asset.objects.get(id=int(form.get('asset_id')))
    except:
        raise RoundException("Asset not found.")
    if 'value' not in form:
        v = models.Vote(
            asset=asset, session=session, type=form.get('vote_type'))
    else:
        v = models.Vote(asset=asset, session=session, value=int(
            form.get('value')), type=form.get('vote_type'))
    v.save()
    return {"success": True}

# @profile(stats=True)
def get_config(request):
    form = request.GET

    if 'project_id' not in form:
        raise RoundException("a project_id is required for this operation")
    project = models.Project.objects.get(id=form.get('project_id'))
    speakers = models.Speaker.objects.filter(
        project=form.get('project_id')).values()
    audiotracks = models.Audiotrack.objects.filter(
        project=form.get('project_id')).values()

    if 'device_id' not in form or ('device_id' in form and form['device_id'] == ""):
        device_id = str(uuid.uuid4())
    else:
        device_id = form.get('device_id')

    l = models.Language.objects.filter(language_code='en')[0]
    if 'language' in form or ('language' in form and form['language'] == ""):
        try:
            l = models.Language.objects.filter(
                language_code=form.get('language'))[0]
        except:
            pass

    # Get current available CPU as percentage.
    cpu_idle = psutil.cpu_times_percent().idle
    # Demo stream is enabled if enabled project wide or CPU idle is less than
    # CPU limit (default 50%.)
    demo_stream_enabled = project.demo_stream_enabled or cpu_idle < float(
        settings.DEMO_STREAM_CPU_LIMIT)

    # Create a new session if new_session is not equal 'false'
    create_new_session = form.get('new_session') != 'false'

    session_id = 0
    if create_new_session:
        s = models.Session(
            device_id=device_id, starttime=datetime.datetime.now(), project=project, language=l)
        if 'client_type' in form:
            s.client_type = form.get('client_type')
        if 'client_system' in form:
            s.client_system = form.get('client_system')
        s.demo_stream_enabled = demo_stream_enabled

        s.save()
        session_id = s.id
        log_event('start_session', s.id, None)

    sharing_message = t("none set", project.sharing_message_loc, l)
    out_of_range_message = t("none set", project.out_of_range_message_loc, l)
    legal_agreement = t("none set", project.legal_agreement_loc, l)
    demo_stream_message = t("none set", project.demo_stream_message_loc, l)

    response = [
        {"device": {"device_id": device_id}},
        # TODO: This should be changed with a schema change to either add it to
        # the project table or create a new news/notification table...or something
        {"notifications": {"startup_message": settings.STARTUP_NOTIFICATION_MESSAGE}},
        {"session": {"session_id": session_id}},
        {"project": {
            "project_id": project.id,
            "project_name": project.name,
            "audio_format": project.audio_format,
            "max_recording_length": project.max_recording_length,
            "recording_radius": project.recording_radius,
            "sharing_message": sharing_message,
            "out_of_range_message": out_of_range_message,
            "sharing_url": project.sharing_url,
            "listen_questions_dynamic": project.listen_questions_dynamic,
            "speak_questions_dynamic": project.speak_questions_dynamic,
            "listen_enabled": project.listen_enabled,
            "geo_listen_enabled": project.geo_listen_enabled,
            "speak_enabled": project.speak_enabled,
            "geo_speak_enabled": project.geo_speak_enabled,
            "reset_tag_defaults_on_startup": project.reset_tag_defaults_on_startup,
            "legal_agreement": legal_agreement,
            "files_url": project.files_url,
            "files_version": project.files_version,
            "audio_stream_bitrate": project.audio_stream_bitrate,
            "demo_stream_enabled": demo_stream_enabled,
            "demo_stream_url": project.demo_stream_url,
            "demo_stream_message": demo_stream_message,
            "latitude": project.latitude,
            "longitude": project.longitude
        }
        },
        {"server": {"version": "2.0"}},
        {"speakers": [dict(d) for d in speakers]},
        {"audiotracks": [dict(d) for d in audiotracks]}
    ]

    return response


# @profile(stats=True)
def get_tags_for_project(request):
    form = request.GET
    p = None
    s = None
    if 'project_id' not in form and 'session_id' not in form:
        raise RoundException(
            "either a project_id or session_id is required for this operation")

    if 'project_id' in form:
        p = models.Project.objects.get(id=form.get('project_id'))
    if 'session_id' in form:
        s = models.Session.objects.get(id=form.get('session_id'))
    return get_config_tags(p, s)


# get_available_assets
# args (project_id, [latitude], [longitude], [radius], [tagids,], [tagbool], [language], [asset_id,...], [envelope_id,...], [...])
# can pass additional parameters matching name of fields on Asset
# example: http://localhost/roundware/?operation=get_available_assets
# returns Dictionary
# @profile(stats=True)
def get_available_assets(request):
    """Return JSON serializable dictionary with the number of matching assets
    by media type and a list of available assets based on filter criteria passed in
    request.  If asset_id is passed, ignore other filters and return single
    asset.  If multiple, comma-separated values for asset_id are passed, ignore
    other filters and return all those assets.  If envelope_id is passed, ignore
    other filters and return all assets in that envelope.  If multiple,
    comma-separated values for envelope_id are passed, ignore
    other filters and return all those assets.  Returns localized
    value for tag strings on asset by asset basis unless a specific language
    code is passed. Fall back to English if necessary."""

    def _get_best_localized_string(asset, tag, best_lang_id):
        """ Return localized string with specified language code.
            If that's not available, look for a language field on the model and
            use that.  If that's not available, fall back to English.
        """
        try:
            localization = tag.loc_msg.get(language=best_lang_id)
        except models.LocalizedString.DoesNotExist:
            # try object's specified language
            asset_lang = asset.language
            if asset_lang and retlng != asset_lang:
                localization = tag.loc_msg.get(language=asset_lang)
            else:
                # fall back to English
                eng_id = models.Language.objects.get(language_code='en')
                localization = tag.loc_msg.get(language=eng_id)
        return localization.localized_string

    form = request.GET
    kw = {}

    known_params = ['project_id', 'latitude', 'longitude',
                    'tag_ids', 'tagbool', 'radius', 'language', 'asset_id',
                    'envelope_id']
    project_id = get_parameter_from_request(request, 'project_id')
    asset_id = get_parameter_from_request(request, 'asset_id')
    envelope_id = get_parameter_from_request(request, 'envelope_id')
    latitude = get_parameter_from_request(request, 'latitude')
    longitude = get_parameter_from_request(request, 'longitude')
    radius = get_parameter_from_request(request, 'radius')
    tag_ids = get_parameter_from_request(request, 'tagids')
    tagbool = get_parameter_from_request(request, 'tagbool')
    language = get_parameter_from_request(request, 'language')
    if (latitude and not longitude) or (longitude and not latitude):
        raise RoundException(
            "This operation requires that you pass both latitude and "
            "longitude, if you pass either one.")

    # accept other keyword parameters as long as the keys are fields on
    # Asset model
    asset_fields = models.get_field_names_from_model(models.Asset)
    asset_media_types = [tup[0] for tup in models.Asset.ASSET_MEDIA_TYPES]
    extraparams = [(param[0], param[1]) for param in form.items()
                   if param[0] not in known_params and
                   param[0] in asset_fields]
    extras = {}
    for k, v in extraparams:
        extras[str(k)] = str(v)

    # if a language (code) is specified, use that
    # otherwise, return localized value specific to Asset
    qry_retlng = None
    if language:
        try:
            qry_retlng = models.Language.objects.get(language_code=language)
            lng_id = models.Language.objects.get(language_code=language)
        except models.Language.DoesNotExist:
            raise RoundException("Specified language code does not exist.")
    else:
        # default to English if no language parameter present
        lng_id = 1

    if asset_id:
        # ignore all other filter criteria
        assets = models.Asset.objects.filter(id__in=asset_id.split(','))

    elif envelope_id:
        assets = []
        envelopes = models.Envelope.objects.filter(
            id__in=envelope_id.split(','))
        for e in envelopes:
            e_assets = e.assets.all()
            for a in e_assets:
                if a not in assets:
                    assets.append(a)

    elif project_id:
        project = models.Project.objects.get(id=project_id)
        kw['project__exact'] = project

        assets = models.Asset.objects.filter(**kw)
        if tag_ids:
            if tagbool and str(tagbool).lower() == 'or':
                assets = assets.filter(
                    tags__in=tag_ids.split(',')).distinct()
            else:
                # 'and'.  Asset must have all tags
                for tag_id in tag_ids.split(','):
                    assets = assets.filter(tags__id=tag_id)

        # filter by extra params. These are chained with an AND
        assets = assets.filter(**extras)

        if latitude and longitude: # need both
            # return only assets within specified or default radius
            # by project
            latitude = float(latitude)
            longitude = float(longitude)
            if not radius:
                radius = project.recording_radius
                if not radius:
                    raise RoundException("Project does not specify a "
                                         "radius and no radius parameter "
                                         "passed to operation.")
            radius = float(radius)
            for asset in assets:
                distance = gpsmixer.distance_in_meters(
                    latitude, longitude,
                    asset.latitude, asset.longitude)
                if distance > radius:
                    assets = assets.exclude(id=asset.id)
    else:
        raise RoundException("This operation requires that you pass a "
                             "project_id, asset_id, or envelope_id")


    assets_info = {}
    assets_info['number_of_assets'] = {}
    for mtype in asset_media_types:
        assets_info['number_of_assets'][mtype] = 0
    assets_list = []

    for asset in assets:
        loc_desc = t("", asset.loc_description, lng_id)

        if asset.mediatype in asset_media_types:
            assets_info['number_of_assets'][asset.mediatype] += 1
        if not qry_retlng:
            retlng = asset.language # can be None
        else:
            retlng = qry_retlng
        assets_list.append(
            dict(asset_id=asset.id,
                 asset_url='%s%s' % (
                     settings.MEDIA_URL, asset.filename),
                 latitude=asset.latitude,
                 longitude=asset.longitude,
                 audio_length=asset.audiolength,
                 submitted=asset.submitted,
                 mediatype=asset.mediatype,
                 description=asset.description,
                 loc_description=loc_desc,
                 project=asset.project.name,
                 language=asset.language.language_code,
                 tags=[dict(
                     tag_category_name=tag.tag_category.name,
                     tag_id=tag.id,
                     localized_value=_get_best_localized_string(
                         asset, tag, retlng)
                 ) for tag in asset.tags.all()]),
        )
    assets_info['assets'] = assets_list
    return assets_info

def op_log_event(request):
    form = request.GET
    if 'session_id' not in form:
        raise RoundException("a session_id is required for this operation")
    if 'event_type' not in form:
        raise RoundException("an event_type is required for this operation")
    log_event(form.get('event_type'), form.get('session_id'), form)

    return {"success": True}

# Used by server.py many times and stream.py once!
def log_event(event_type, session_id, requestget=None):
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
    if requestget:
        client_time = requestget.get("client_time", None)
        latitude = requestget.get("latitude", None)
        longitude = requestget.get("longitude", None)
        tags = requestget.get("tags", None)
        data = requestget.get("data", None)

    e = models.Event(session=s,
              event_type=event_type,
              server_time=datetime.datetime.now(),
              client_time=client_time,
              latitude=latitude,
              longitude=longitude,
              tags=tags,
              data=data)
    e.save()

# create_envelope
# args: (operation, session_id, [tags])
# example: http://localhost/roundware/?operation=create_envelope&sessionid=1&tags=1,2
# returns envelope_id, sharing_messsage
# example:
#{"envelope_id": 2}

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
# args (operation, envelope_id, file, latitude, longitude, [tagids])
# example: http://localhost/roundware/?operation=add_asset_to_envelope
# OR
# add_asset_to_envelope (GET method)
# args (operation, envelope_id, asset_id) #asset_id must point to an Asset that exists in the database
# returns success bool
# {"success": true}
# @profile(stats=True)
def add_asset_to_envelope(request):

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

    envelope_id = get_parameter_from_request(request, 'envelope_id', True)
    logger.debug("Found asset_id: %d, envelope_id: %d", asset_id, envelope_id)

    try:
        envelope = models.Envelope.objects.select_related(
            'session').get(id=envelope_id)
    except models.Envelope.DoesNotExist:
        raise RoundException(
            "Invalid Envelope ID Provided. No Envelope exists with ID %s" % envelope_id)

    session = envelope.session

    log_event("start_upload", session.id, request.GET)

    fileitem = asset.file if asset else request.FILES.get('file')
    if not fileitem.name:
        raise RoundException("No file in request")

    # get mediatype from the GET request
    mediatype = get_parameter_from_request(
        request, 'mediatype') if not asset else asset.mediatype
    # if mediatype parameter not passed, set to 'audio'
    # this ensures backwards compatibility
    if mediatype is None:
        mediatype = "audio"

    # copy the file to a unique name (current time and date)
    logger.debug("Processing " + fileitem.name)
    (filename_prefix, filename_extension) = os.path.splitext(fileitem.name)

    dest_filename = time.strftime("%Y%m%d-%H%M%S-") + str(session.id) + \
        filename_extension
    dest_filepath = os.path.join(settings.MEDIA_ROOT, dest_filename)
    if os.path.isfile(dest_filepath):
        raise RoundException("File already exists: %s" %
                                            dest_filepath)


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
        if tags is not None:
            ids = tags.split(',')
            tagset = models.Tag.objects.filter(id__in=ids)

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

        asset = models.Asset(latitude=latitude,
                             longitude=longitude,
                             filename=newfilename,
                             session=session,
                             submitted=submitted,
                             mediatype=mediatype,
                             volume=1.0,
                             language=session.language,
                             project=session.project)
        asset.file.name = dest_filename
        asset.save()
        for t in tagset:
            asset.tags.add(t)


    # get the audiolength of the file only if mediatype is audio and
    # update the Asset
    if mediatype == "audio":
        discover_audiolength.discover_and_set_audiolength(
            asset, newfilename)
        asset.save()

    envelope.assets.add(asset)
    envelope.save()

    rwdbus_send.emit_stream_signal(0, "refresh_recordings", "")
    return {"success": True,
            "asset_id": asset.id}


def get_parameter_from_request(request, name, required=False):
    ret = None
    try:
        ret = request.POST[name]
    except (KeyError, AttributeError):
        try:
            ret = request.GET[name]
        except (KeyError, AttributeError):
            if required:
                raise RoundException(
                    name + " is required for this operation")
    return ret

# @profile(stats=True)
def request_stream(request):
    session_id = request.GET.get('session_id', None)
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

def modify_stream(request):
    success = False
    msg = ""
    # TODO: Why is this request data changed so much? Why isn't msg used?
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
            rwdbus_send.emit_stream_signal(
                int(form['session_id']), "modify_stream", arg_hack)
            success = True
        else:
            msg = "no stream available for session: " + form['session_id']
    else:
        msg = "a session_id is required for this operation"

    if success:
        return {"success": success}
    else:
        return {"success": success}


def move_listener(request):
    form = request.GET
    request = form_to_request(form)
    arg_hack = json.dumps(request)
    log_event("move_listener", int(form['session_id']), form)
    rwdbus_send.emit_stream_signal(
        int(form['session_id']), "move_listener", arg_hack)
    return {"success": True}


def heartbeat(request):
    form = request.GET
    rwdbus_send.emit_stream_signal(int(form['session_id']), "heartbeat", "")
    log_event("heartbeat", int(form['session_id']), form)
    return {"success": True}


def current_version(request):
    """
    Returns the current API version number
    """
    return {"version": "2.0"}


def get_events(request):
    """
    Return all events for the specified session_id
    """
    form = request.GET
    if 'session_id' in form:
        session = models.Session.objects.get(id=form['session_id'])
        events = models.Event.objects.filter(session=form['session_id'])
        events_info = {}
        events_info['number_of_events'] = 0
        events_list = []

        for e in events:
            events_list.append(
                dict(event_id=e.id,
                     session_id=e.session_id,
                     event_type=e.event_type,
                     latitude=e.latitude,
                     longitude=e.longitude,
                     data=e.data,
                     tags=e.tags,
                     server_time=str(e.server_time),
                     )
            )
            events_info['number_of_events'] += 1

        events_info['events'] = events_list
        events_info['project_id'] = session.project.id
        return events_info
    else:
        return {"error": "no session_id"}

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


def stream_exists(sessionid, audio_format):
    admin = icecast2.Admin()
    return admin.stream_exists(icecast2.mount_point(sessionid, audio_format))


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


def form_to_request(form):
    request = {}
    for p in ['project_id', 'session_id', 'asset_id']:
        if p in form and form[p]:
            request[p] = map(int, form[p].split("\t"))
        else:
            request[p] = []
    for p in ['tags']:
        if p in form and form[p]:
            # make sure we don't have blank values from trailing commas
            p_list = [v for v in form[p].split(",") if v != ""]
            request[p] = map(int, p_list)
        else:
            request[p] = []

    for p in ['latitude', 'longitude']:
        if p in form and form[p]:
            request[p] = float(form[p])
        else:
            request[p] = False
    return request


# @profile(stats=True)
def get_config_tags(p=None, s=None):
    if s is None and p is None:
        raise RoundException("Must pass either a project or "
                                            "a session")
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

            masterD = {'name': masterui.name, 'header_text': header, 'code': masterui.tag_category.name,
                       'select': masterui.select.name, 'order': masterui.index}
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
            if masterui.ui_mode.name not in modes:
                modes[masterui.ui_mode.name] = [masterD, ]
            else:
                modes[masterui.ui_mode.name].append(masterD)

    return modes
