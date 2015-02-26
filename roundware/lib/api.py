from __future__ import unicode_literals
from roundware.rw import models
from roundware.lib import dbus_send
from roundware.lib.exception import RoundException
from roundwared import gpsmixer
from roundwared import icecast2
from django.conf import settings
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
        form = request.data
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


def move_listener(request, context=None):
    if context is not None and "pk" in context:
        form = request.data
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
