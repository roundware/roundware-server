# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
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
from roundware.lib import dbus_send
from roundware.lib.exception import RoundException
from roundwared import gpsmixer
from roundware.lib.api import (get_project_tags, t, log_event, form_to_request,
                               check_for_single_audiotrack, get_parameter_from_request)

logger = logging.getLogger(__name__)


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
    dbus_send.emit_stream_signal(
        int(form['session_id']), "play_asset", arg_hack)
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
    return get_project_tags(p, s)


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
            try:
                if asset_lang and best_lang_id != asset_lang:
                    localization = tag.loc_msg.get(language=asset_lang)
                else:
                    # fall back to English
                    english = models.Language.objects.get(language_code='en')
                    localization = tag.loc_msg.get(language=english)
            except models.LocalizedString.DoesNotExist:
                # Worst case return the unlocalized value.
                # Yes, Tag.loc_msg = Tag.value.
                return tag.value
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

        if latitude and longitude:  # need both
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
            retlng = asset.language  # can be None
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
