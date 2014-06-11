#***********************************************************************************#

# ROUNDWARE
# a contributory, location-aware media platform

# Copyright (C) 2008-2014 Halsey Solutions, LLC
# with contributions from:
# Mike MacHenry, Ben McAllister, Jule Slootbeek and Halsey Burgund (halseyburgund.com)
# http://roundware.org | contact@roundware.org

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/lgpl.html>.

#***********************************************************************************#


import time
import subprocess
import os
import logging
import json
import uuid
import datetime
import psutil
try:
    from profiling import profile
except ImportError:
    pass
from roundwared import settings
from roundwared import db
from roundwared import convertaudio
from roundwared import discover_audiolength
from roundwared import roundexception
from roundwared import icecast2
from roundwared import gpsmixer
from roundwared import rounddbus
from roundware.rw import models
from roundware import settings as rw_settings

def check_for_single_audiotrack(session_id):
    ret = False
    session = models.Session.objects.select_related('project').get(id=session_id)
    tracks = models.Audiotrack.objects.filter(project=session.project)
    if tracks.count() == 1:
        ret = True
    return ret

#2.1 Protocol additions AS 1.2


def get_current_streaming_asset(request):
    form = request.GET
    if not form.has_key('session_id'):
        raise roundexception.RoundException("a session_id is required for this operation")
    if check_for_single_audiotrack(form.get('session_id')) != True:
        raise roundexception.RoundException("this operation is only valid for projects with 1 audiotrack")
    else:
        l = db.get_current_streaming_asset(form.get('session_id'))
    if l:
        return {"asset_id": l.asset.id,
                "start_time": l.starttime.isoformat(),
                "duration_in_stream": l.duration / 1000000,
                "current_server_time": datetime.datetime.now().isoformat()}
    else:
        return {"user_error_message": "no asset found"}


def get_asset_info(request):
    form = request.GET
    if not form.has_key('asset_id'):
        raise roundexception.RoundException("an asset_id is required for this operation")

    if check_for_single_audiotrack(form.get('session_id')) != True:
        raise roundexception.RoundException("this operation is only valid for projects with 1 audiotrack")
    else:
        a = db.get_asset(form.get('asset_id'))
    if a:
        return {"asset_id": a.id,
                "created": a.created.isoformat(),
                "duraton_in_ms": a.audiolength / 1000000}
    else:
        return {"user_error_message": "asset not found"}

def play_asset_in_stream(request):
    form = request.GET
    # add skipped asset_id to form in order to track which asset is played
    #assetid = form[asset_id]
    #form[data] = form["asset_id"]
    request = form_to_request(form)
    arg_hack = json.dumps(request)
    db.log_event("play_asset_in_stream", int(form['session_id']), form)

    if not form.has_key('session_id'):
        raise roundexception.RoundException("a session_id is required for this operation")
    if check_for_single_audiotrack(form.get('session_id')) != True:
        raise roundexception.RoundException("this operation is only valid for projects with 1 audiotrack")
    if not form.has_key('asset_id'):
        raise roundexception.RoundException("an asset_id is required for this operation")
    rounddbus.emit_stream_signal(int(form['session_id']), "play_asset", arg_hack)
    return {"success": True}


def skip_ahead(request):
    form = request.GET
    db.log_event("skip_ahead", int(form['session_id']), form)

    if not form.has_key('session_id'):
        raise roundexception.RoundException("a session_id is required for this operation")
    if check_for_single_audiotrack(form.get('session_id')) != True:
        raise roundexception.RoundException("this operation is only valid for projects with 1 audiotrack")
    rounddbus.emit_stream_signal(int(form['session_id']), "skip_ahead", "")
    return {"success": True}

def vote_asset(request):
    form = request.GET
    db.log_event("vote_asset", int(form['session_id']), form)

    if not form.has_key('session_id'):
        raise roundexception.RoundException("a session_id is required for this operation")
    if not form.has_key('asset_id'):
        raise roundexception.RoundException("an asset_id is required for this operation")
    if not form.has_key('vote_type'):
        raise roundexception.RoundException("a vote_type is required for this operation")
    if check_for_single_audiotrack(form.get('session_id')) != True:
        raise roundexception.RoundException("this operation is only valid for projects with 1 audiotrack")

    try:
        session = models.Session.objects.get(id=int(form.get('session_id')))
    except:
        raise roundexception.RoundException("Session not found.")
    try:
        asset = models.Asset.objects.get(id=int(form.get('asset_id')))
    except:
        raise roundexception.RoundException("asset not found.")
    if not form.has_key('value'):
        v = models.Vote(asset=asset, session=session, type=form.get('vote_type'))
    else:
        v = models.Vote(asset=asset, session=session, value=int(form.get('value')), type=form.get('vote_type'))
    v.save()
    return {"success": True}

#2.0 Protocol


# @profile(stats=True)
def get_config(request):
    form = request.GET
    try:
        hostname_without_port = str(settings.config["external_host_name_without_port"])
    except KeyError:
        raise roundexception.RoundException("Roundware configuration file is missing 'external_host_name_without_port' key. ")
    #check params
    if not form.has_key('project_id'):
        raise roundexception.RoundException("a project_id is required for this operation")
    project = models.Project.objects.get(id=form.get('project_id'))
    speakers = models.Speaker.objects.filter(project=form.get('project_id')).values()
    audiotracks = models.Audiotrack.objects.filter(project=form.get('project_id')).values()

    if not form.has_key('device_id') or (form.has_key('device_id') and form['device_id'] == ""):
        device_id = str(uuid.uuid4())
    else:
        device_id = form.get('device_id')

    l = models.Language.objects.filter(language_code='en')[0]
    if form.has_key('language') or (form.has_key('language') and form['language'] == ""):
        try:
            l = models.Language.objects.filter(language_code=form.get('language'))[0]
        except:
            pass

    s = models.Session(device_id=device_id, starttime=datetime.datetime.now(), project=project, language=l)
    if form.has_key('client_type'):
        s.client_type = form.get('client_type')
    if form.has_key('client_system'):
        s.client_system = form.get('client_system')


    sharing_url = str.format("http://{0}/roundware/?operation=view_envelope&envelopeid=[id]", hostname_without_port)
    sharing_message = "none set"
    out_of_range_message = "none set"
    legal_agreement = "none set"
    demo_stream_message = "none set"
    try:
        sharing_message = project.sharing_message_loc.filter(language=l)[0].localized_string
    except:
        pass
    try:
        out_of_range_message = project.out_of_range_message_loc.filter(language=l)[0].localized_string
    except:
        pass
    try:
        legal_agreement = project.legal_agreement_loc.filter(language=l)[0].localized_string
    except:
        pass
    try:
        demo_stream_message = project.demo_stream_message_loc.filter(language=l)[0].localized_string
    except:
        pass

    cpu_idle = psutil.cpu_times_percent().idle
    s.demo_stream_enabled = project.demo_stream_enabled or cpu_idle < float(settings.config["demo_stream_cpu_limit"])

    s.save()
    session_id = s.id

    response = [
            {"device":{"device_id": device_id}},
            {"session":{"session_id": session_id}},
            {"project":{
                    "project_id":project.id,
                    "project_name":project.name,
                    "audio_format":project.audio_format,
                    "max_recording_length":project.max_recording_length,
                    "recording_radius":project.recording_radius,
                    "sharing_message":sharing_message,
                    "out_of_range_message":out_of_range_message,
                    "sharing_url":project.sharing_url,
                    "listen_questions_dynamic":project.listen_questions_dynamic,
                    "speak_questions_dynamic":project.speak_questions_dynamic,
                    "listen_enabled":project.listen_enabled,
                    "geo_listen_enabled":project.geo_listen_enabled,
                    "speak_enabled":project.speak_enabled,
                    "geo_speak_enabled":project.geo_speak_enabled,
                    "reset_tag_defaults_on_startup":project.reset_tag_defaults_on_startup,
                    "legal_agreement":legal_agreement,
                    "files_url":project.files_url,
                    "files_version":project.files_version,
                    "audio_stream_bitrate":project.audio_stream_bitrate,
                    # TODO: following attribute 'demo_stream_enabled' has been moved to the 'session' object
                    "demo_stream_enabled":s.demo_stream_enabled,
                    "demo_stream_url":project.demo_stream_url,
                    "demo_stream_message":demo_stream_message,
                    "latitude":project.latitude,
                    "longitude":project.longitude
                    }},

            {"server":{
                    "version": "2.0"}},
            {"speakers":[dict(d) for d in speakers]},
            {"audiotracks":[dict(d) for d in audiotracks]}
    ]
    db.log_event('start_session', session_id, None)
    return response


# @profile(stats=True)
def get_tags_for_project(request):
    form = request.GET
    p = None
    s = None
    if not form.has_key('project_id') and not form.has_key('session_id'):
        raise roundexception.RoundException("either a project_id or session_id is required for this operation")

    if form.has_key('project_id'):
        p = models.Project.objects.get(id=form.get('project_id'))
    if form.has_key('session_id'):
        s = models.Session.objects.get(id=form.get('session_id'))
    return db.get_config_tag_json(p, s)


#get_available_assets
#args (project_id, [latitude], [longitude], [radius], [tagids,], [tagbool], [language], [asset_id,...], [envelope_id,...], [...])
#can pass additional parameters matching name of fields on Asset
#example: http://localhost/roundware/?operation=get_available_assets
#returns Dictionary
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
    try:
        hostname_without_port = str(settings.config["external_host_name_without_port"])
    except KeyError:
        raise roundexception.RoundException("Roundware configuration file is missing 'external_host_name_without_port' key. ")

    known_params = ['project_id', 'latitude', 'longitude',
                    'tag_ids', 'tagbool', 'radius', 'language', 'asset_id',
                    'envelope_id' ]
    project_id = get_parameter_from_request(request, 'project_id', None)
    asset_id = get_parameter_from_request(request, 'asset_id', None)
    envelope_id = get_parameter_from_request(request, 'envelope_id', None)
    latitude = get_parameter_from_request(request, 'latitude', None)
    longitude = get_parameter_from_request(request, 'longitude', None)
    radius = get_parameter_from_request(request, 'radius', None)
    tag_ids = get_parameter_from_request(request, 'tagids', None)
    tagbool = get_parameter_from_request(request, 'tagbool', None)
    language = get_parameter_from_request(request, 'language', None)
    if (latitude and not longitude) or (longitude and not latitude):
        raise roundexception.RoundException(
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
            raise roundexception.RoundException(
                "Specified language code does not exist."
            )
    else:
        # default to Emglish if no language parameter present
        lng_id = 1

    if project_id or asset_id or envelope_id:

        # by asset
        if asset_id:
            # ignore all other filter criteria
            assets = models.Asset.objects.filter(id__in=asset_id.split(','))

        # by envelope
        elif envelope_id:
            assets = []
            envelopes = models.Envelope.objects.filter(id__in=envelope_id.split(','))
            for e in envelopes:
                e_assets = e.assets.all()
                for a in e_assets:
                    if a not in assets:
                        assets.append(a)

        # by project
        elif project_id:
            project = models.Project.objects.get(id=project_id)
            kw['project__exact'] = project

            assets = models.Asset.objects.filter(**kw)
            if tag_ids:
                if tagbool and str(tagbool).lower() == 'or':
                    assets = assets.filter(tags__in=tag_ids.split(',')).distinct()
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
                        raise roundexception.RoundException("Project does not "
                            "specify a radius and no radius parameter passed to "
                            "operation.")
                radius = float(radius)
                for asset in assets:
                    distance = gpsmixer.distance_in_meters(
                        latitude, longitude,
                        asset.latitude, asset.longitude)
                    if distance > radius:
                        assets = assets.exclude(id=asset.id)

        assets_info = {}
        assets_info['number_of_assets'] = {}
        for mtype in asset_media_types:
            assets_info['number_of_assets'][mtype]= 0
        assets_list = []

        for asset in assets:
            temp_desc = ""
            loc_desc = ""
            temp_desc = asset.loc_description.filter(language=lng_id)
            if temp_desc:
                loc_desc = temp_desc[0].localized_string
            if asset.mediatype in asset_media_types:
                assets_info['number_of_assets'][asset.mediatype] +=1
            if not qry_retlng:
                retlng = asset.language # can be None
            else:
                retlng = qry_retlng
            assets_list.append(
                dict(asset_id=asset.id,
                     asset_url='%s%s' % (
                         rw_settings.AUDIO_FILE_URI, asset.filename),
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

    else:
        raise roundexception.RoundException("This operation requires that you "
            "pass a project_id, asset_id, or envelope_id")

def log_event(request):

    form = request.GET
    if not form.has_key('session_id'):
        raise roundexception.RoundException("a session_id is required for this operation")
    if not form.has_key('event_type'):
        raise roundexception.RoundException("an event_type is required for this operation")
    db.log_event(form.get('event_type'), form.get('session_id'), form)

    return {"success": True}

#create_envelope
#args: (operation, session_id, [tags])
#example: http://localhost/roundware/?operation=create_envelope&sessionid=1&tags=1,2
#returns envelope_id, sharing_messsage
#example:
#{"envelope_id": 2}

# @profile(stats=True)
def create_envelope(request):
    form = request.GET
    if not form.has_key('session_id'):
        raise roundexception.RoundException("a session_id is required for this operation")
    s = models.Session.objects.get(id=form.get('session_id'))

    #todo - tags

    env = models.Envelope(session=s)
    env.save()

    return {"envelope_id": env.id}

#add_asset_to_envelope (POST method)
#args (operation, envelope_id, file, latitude, longitude, [tagids])
#example: http://localhost/roundware/?operation=add_asset_to_envelope
# OR
#add_asset_to_envelope (GET method)
#args (operation, envelope_id, asset_id) #asset_id must point to an Asset that exists in the database
#returns success bool
#{"success": true}
# @profile(stats=True)
def add_asset_to_envelope(request):

    #get asset_id from the GET request
    asset_id = get_parameter_from_request(request, 'asset_id', False)
    asset = None
    #grab the Asset from the database, if an asset_id has been passed in
    if asset_id:
        try:
            asset = models.Asset.objects.get(pk=asset_id)
        except models.Asset.DoesNotExist:
            raise roundexception.RoundException("Invalid Asset ID Provided. No Asset exists with ID %s" % asset_id)
    envelope_id = get_parameter_from_request(request, 'envelope_id', True)

    envelope = models.Envelope.objects.select_related('session').get(id=envelope_id)
    session = envelope.session

    db.log_event("start_upload", session.id, request.GET)

    fileitem = request.FILES.get('file') if not asset else asset.file
    #get mediatype from the GET request
    mediatype = get_parameter_from_request(request, 'mediatype', False) if not asset else asset.mediatype
    #if mediatype parameter not passed, set to 'audio'
    #this ensures backwards compatibility
    if mediatype is None:
        mediatype = "audio"

    if fileitem.name:
        #copy the file to a unique name (current time and date)
        logging.debug("Processing " + fileitem.name)
        (filename_prefix, filename_extension) = \
            os.path.splitext(fileitem.name)
        fn = time.strftime("%Y%m%d-%H%M%S") + filename_extension
        fileout = open(os.path.join(settings.config["upload_dir"], fn), 'wb')
        fileout.write(fileitem.file.read())
        fileout.close()
        #delete the uploaded original after the copy has been made
        if asset:
            asset.file.delete()
            # re-assign file to asset
            asset.file.name = fn
            asset.filename = fn
            asset.save()
        #make sure everything is in wav form only if mediatype is audio
        if mediatype == "audio":
            newfilename = convertaudio.convert_uploaded_file(fn)
        else:
            newfilename = fn
        if newfilename:
            #create the new asset if request comes in from a source other
            #than the django admin interface
            if not asset:
                #get location data from request
                latitude = get_parameter_from_request(request, 'latitude', False)
                longitude = get_parameter_from_request(request, 'longitude', False)
                #if no location data in request, default to project latitude and longitude
                if not latitude:
                    latitude = session.project.latitude
                if not longitude:
                    longitude = session.project.longitude
                tagset = []
                tags = get_parameter_from_request(request, 'tags', False)
                if tags is not None:
                    ids = tags.split(',')
                    tagset = models.Tag.objects.filter(id__in=ids)

                # get optional submitted parameter from request (Y, N or blank string are only acceptable values)
                submitted = get_parameter_from_request(request, 'submitted', False)
                # set submitted variable to proper boolean value if it is passed as parameter
                if submitted == "N":
                    submitted = False
                elif submitted == "Y":
                    submitted = True
                # if blank string or not included as parameter, check if in range of project and if so
                # set asset.submitted based on project.auto_submit boolean value
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
                                     project = session.project)
                asset.file.name = fn
                asset.save()
                for t in tagset:
                    asset.tags.add(t)
            #if the request comes from the django admin interface
            #update the Asset with the right information
            else:
                #update asset with session
                asset.session = session
                asset.filename = newfilename

            #get the audiolength of the file only if mediatype is audio and update the Asset
            if mediatype == "audio":
                discover_audiolength.discover_and_set_audiolength(asset, newfilename)
                asset.save()
            envelope.assets.add(asset)
            envelope.save()
        else:
            raise roundexception.RoundException("File not converted successfully: " + newfilename)
    else:
        raise roundexception.RoundException("No file in request")
    rounddbus.emit_stream_signal(0, "refresh_recordings", "")
    return {"success": True,
            "asset_id": asset.id}


def get_parameter_from_request(request, name, required):
    ret = None
    try:
        ret = request.POST[name]
    except (KeyError, AttributeError):
        try:
            ret = request.GET[name]
        except (KeyError, AttributeError):
            if required:
                raise roundexception.RoundException(name + " is required for this operation")
    return ret


# @profile(stats=True)
def request_stream(request):

    request_form = request.GET
    try:
        hostname_without_port = str(settings.config["external_host_name_without_port"])
    except KeyError:
        raise roundexception.RoundException("Roundware configuration file is missing 'external_host_name_without_port' key. ")
    db.log_event("request_stream", int(request_form['session_id']), request_form)

    if not request_form.get('session_id'):
        raise roundexception.RoundException("Must supply session_id.")
    session = models.Session.objects.select_related('project').get(id=request_form.get('session_id'))
    project = session.project

    if session.demo_stream_enabled:
        # return {"success": "demo_stream_enabled"}
        msg = "demo_stream_message"
        try:
            msg = project.demo_stream_message_loc.filter(language=session.language)[0].localized_string
        except:
            pass

        if project.demo_stream_url:
            url = project.demo_stream_url
        else:
            url = "http://" + hostname_without_port + ":" + \
                  str(settings.config["icecast_port"]) + \
                  "/demo_stream.mp3"

        return {
            'stream_url': url,
            'demo_stream_message': msg
        }

    elif is_listener_in_range_of_stream(request_form, project):
        command = ['/usr/pythonenv/roundware-server/bin/streamscript', '--session_id', str(session.id), '--project_id', str(project.id)]
        for p in ['latitude', 'longitude', 'audio_format']:
            if request_form.has_key(p) and request_form[p]:
                command.extend(['--' + p, request_form[p].replace("\t", ",")])
        if request_form.has_key('config'):
            command.extend(['--configfile', os.path.join(settings.configdir, request_form['config'])])
        else:
            command.extend(['--configfile', os.path.join(settings.configdir, 'rw')])
        if request_form.has_key('audio_stream_bitrate'):
            command.extend(['--audio_stream_bitrate', str(request_form['audio_stream_bitrate'])])

        audio_format = project.audio_format.upper()

        apache_safe_daemon_subprocess(command)
        wait_for_stream(session.id, audio_format)

        return {
            "stream_url": "http://" + hostname_without_port + ":" + \
                str(settings.config["icecast_port"]) + \
                icecast_mount_point(session.id, audio_format),
        }
    else:
        msg = "This application is designed to be used in specific geographic locations.  Apparently your phone thinks you are not at one of those locations, so you will hear a sample audio stream instead of the real deal.  If you think your phone is incorrect, please restart Scapes and it will probably work.  Thanks for checking it out!"
        try:
            msg = project.out_of_range_message_loc.filter(language=session.language)[0].localized_string
        except:
            pass

        # if project.out_of_range_url: all projects must have an out
        # of range url
        url = project.out_of_range_url
        # else:
        #     url = "http://" + hostname_without_port + ":" + \
        #                 str(settings.config["icecast_port"]) + \
        #                 "/outofrange.mp3"

        return {
            'stream_url': url,
            'user_message': msg
        }

# @profile(stats=True)
def modify_stream(request):
    success = False
    msg = ""
    form = request.GET
    request = form_to_request(form)
    arg_hack = json.dumps(request)
    db.log_event("modify_stream", int(form['session_id']), form)

    if form.has_key('session_id'):
        session = models.Session.objects.select_related('project').get(id=form['session_id'])
        project = session.project
        if form.has_key('language'):
            try:
                logging.debug("modify_stream: language: " + form['language'])
                l = models.Language.objects.filter(language_code=form['language'])[0]
                session.language = l
                session.save()
            except:
                raise roundexception.RoundException("language not supported")

        audio_format = project.audio_format.upper()
        if stream_exists(int(form['session_id']), audio_format):
            rounddbus.emit_stream_signal(int(form['session_id']), "modify_stream", arg_hack)
            success = True
        else:
            msg = "no stream available for session: " + form['session_id']
    else:
        msg = "a session_id is required for this operation"

    if success:
        return {"success": success}
    else:
        return {"success": success, }


def move_listener(request):
    form = request.GET
    request = form_to_request(form)
    arg_hack = json.dumps(request)
    rounddbus.emit_stream_signal(int(form['session_id']), "move_listener", arg_hack)
    return {"success": True}


def heartbeat(request):
    form = request.GET
    rounddbus.emit_stream_signal(int(form['session_id']), "heartbeat", "")
    db.log_event("heartbeat", int(form['session_id']), form)
    return {"success": True}


def current_version(request):
    return {"version": "2.0"}

def get_events(request):
    form = request.GET
    session_id = form.get('session_id', None)
    events = models.Event.objects.filter(session=session_id)
    # event_types = models.Event.objects.values_list('event_type').distinct()
    events_info = {}
    events_info['number_of_events'] = 0
    # for etype in event_types:
    #     events_info['number_of_events'][etype]= 0
    events_list = []
    if form.has_key('session_id'):
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
            events_info['number_of_events'] +=1
        events_info['events'] = events_list
        return events_info
    else:
        return {"error": "no session_id!!"}

#END 2.0 Protocol

#2.0 Helper methods


def apache_safe_daemon_subprocess(command):
    logging.debug(str(command))
    DEVNULL_OUT = open(os.devnull, 'w')
    DEVNULL_IN = open(os.devnull, 'r')
    proc = subprocess.Popen(
        command,
        close_fds=True,
        stdin=DEVNULL_IN,
        stdout=DEVNULL_OUT,
        stderr=DEVNULL_OUT,
    )
    proc.wait()


# Loops until the give stream is present and ready to be listened to.
def wait_for_stream(sessionid, audio_format):
    logging.debug("waiting " + str(sessionid) + audio_format)
    admin = icecast2.Admin(settings.config["icecast_host"] + ":" + str(settings.config["icecast_port"]),
                           settings.config["icecast_username"],
                           settings.config["icecast_password"])
    retries_left = 1000
    while not admin.stream_exists(icecast_mount_point(sessionid, audio_format)):
        if retries_left > 0:
            retries_left -= 1
        else:
            raise roundexception.RoundException("Stream timedout on creation")
        time.sleep(0.1)


def stream_exists(sessionid, audio_format):
    logging.debug("checking for existence of " + str(sessionid) + audio_format)
    admin = icecast2.Admin(settings.config["icecast_host"] + ":" + str(settings.config["icecast_port"]),
                           settings.config["icecast_username"],
                           settings.config["icecast_password"])
    return admin.stream_exists(icecast_mount_point(sessionid, audio_format))


def is_listener_in_range_of_stream(form, proj):
    if not ('latitude' in form and 'longitude' in form) or not (form['latitude'] and form['longitude']):
        return True
    speakers = models.Speaker.objects.filter(project=proj, activeyn=True)

    for speaker in speakers:
        #only do this if latitude and longitude are included, return False otherwise
        distance = gpsmixer.distance_in_meters(
            float(form['latitude']),
            float(form['longitude']),
            speaker.latitude,
            speaker.longitude)
        if distance < 3 * speaker.maxdistance:
            return True
    return False

#END 2.0 Helper methods


def form_to_request(form):
    request = {}
    for p in ['project_id', 'session_id', 'asset_id']:
        if form.has_key(p) and form[p]:
            request[p] = map(int, form[p].split("\t"))
        else:
            request[p] = []
    for p in ['tags']:
        if form.has_key(p) and form[p]:
            # make sure we don't have blank values from trailing commas
            p_list = [v for v in form[p].split(",") if v != ""]
            request[p] = map(int, p_list)
        else:
            request[p] = []

    for p in ['latitude', 'longitude']:
        if form.has_key(p) and form[p]:
            request[p] = float(form[p])
        else:
            request[p] = False
    return request


def icecast_mount_point(sessionid, audio_format):
    return '/stream' + str(sessionid) + "." + audio_format.lower()
