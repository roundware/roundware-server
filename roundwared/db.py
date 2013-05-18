# ROUNDWARE
# a participatory, location-aware media platform

# Copyright (C) 2008-2013 Halsey Solutions, LLC
# with contributions from:
# Mike MacHenry
# Ben McAllister (listenfaster.com)
# Halsey Burgund (halseyburgund.com)
# http://roundware.org | contact@roundware.org

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import string
import logging
import datetime
import time
from roundwared import settings
from roundwared import gpsmixer
from roundwared import roundexception
from django.db.models import Q
from roundware.rw.models import Session
from roundware.rw.models import Language
from roundware.rw.models import Event
from roundware.rw.models import Project
from roundware.rw.models import Asset
from roundware.rw.models import Tag
from roundware.rw.models import TagCategory
from roundware.rw.models import MasterUI
from roundware.rw.models import UIMapping
from roundware.rw.models import ListeningHistoryItem
from roundwared import icecast2
import operator
import pycurl


def get_config_tag_json(p, s):
    lingo = Language.objects.filter(language_code='en')[0]
    if s != None:
        p = s.project
        lingo = s.language

    m = MasterUI.objects.filter(project=p)
    response = []
    modes = {}
    for masterui in m:
        if masterui.active:
            mappings = UIMapping.objects.filter(master_ui=masterui, active=True)
            if masterui.header_text_loc.all():
                ht = masterui.header_text_loc.filter(language=lingo)[0].localized_string
            else:
                ht = ""
            #masterD = masterui.toTagDictionary()
            masterD = {'name': masterui.name, 'header_text': ht, 'code': masterui.tag_category.name,
                       'select': masterui.select.name, 'order': masterui.index}
            masterOptionsList = []

            default = []
            for mapping in mappings:
                if mapping.default:
                    default.append(mapping.tag.id)
                #masterOptionsList.append(mapping.toTagDictionary())
                #def toTagDictionary(self):
                    #return {'tag_id':self.tag.id,'order':self.index,'value':self.tag.value}

                masterOptionsList.append({'tag_id': mapping.tag.id, 'order': mapping.index, 'data': mapping.tag.data,
                                          'relationships': mapping.tag.get_relationships(),
                                          'value': mapping.tag.loc_msg.filter(language=lingo)[0].localized_string})
            masterD["options"] = masterOptionsList
            masterD["defaults"] = default
            if not modes.has_key(masterui.ui_mode.name):
                modes[masterui.ui_mode.name] = [masterD, ]
            else:
                modes[masterui.ui_mode.name].append(masterD)

    return modes


def get_recordings(request):

    logging.debug("get_recordings: got request: " + str(request))
    recs = []
    p = None
    s = None
    if request.has_key("project_id") and hasattr(request["project_id"], "__iter__") and len(request["project_id"]) > 0:
        logging.debug("get_recordings: got project_id: " + str(request["project_id"][0]))
        p = Project.objects.get(id=request["project_id"][0])
    elif request.has_key("project_id") and not hasattr(request["project_id"], "__iter__"):
        logging.debug("get_recordings: got project_id: " + str(request["project_id"]))
        p = Project.objects.get(id=request["project_id"])

    if request.has_key("session_id") and hasattr(request["session_id"], "__iter__") and len(request["session_id"]) > 0:
        logging.debug("get_recordings: got session_id: " + str(request["session_id"][0]))
        s = Session.objects.get(id=request["session_id"][0])
        p = s.project
    elif request.has_key("session_id") and not hasattr(request["session_id"], "__iter__"):
        logging.debug("get_recordings: got session_id: " + str(request["session_id"]))
        s = Session.objects.get(id=request["session_id"])
        p = s.project

    # this first check checks whether tags is a list of numbers.
    if request.has_key("tags") and hasattr(request["tags"], "__iter__") and len(request["tags"]) > 0:
        logging.debug("get_recordings: got " + str(len(request["tags"])) + "tags.")
        #recs = Asset.objects.filter(project=p, submitted=True, tags__in=request["tags"])
        recs = filter_recs_for_tags(p, request["tags"], s.language)
    # this second check checks whether tags is a string representation of a list of numbers.
    elif request.has_key("tags") and not hasattr(request["tags"], "__iter__"):
        logging.debug("get_recordings: tags supplied: " + request["tags"])
        #recs = Asset.objects.filter(project=p,submitted=True, tags__in=request["tags"].split(","))
        recs = filter_recs_for_tags(p, request["tags"].split(","), s.language)
    else:
        logging.debug("get_recordings: no tags supplied")
        if s != None:
            recs = Asset.objects.filter(project=p, submitted=True, audiolength__gt=1000, language=s.language).distinct()
            recs = filter_recs_for_tags(p, get_default_tags_for_project(p, s), s.language)

    logging.debug("db: get_recordings: got " + str(len(recs)) + " recordings from db for project " + str(p.id))
    return recs


def get_default_tags_for_project(p, s):
    lingo = Language.objects.filter(language_code='en')[0]
    if s != None:
        p = s.project
        lingo = s.language

    m = MasterUI.objects.filter(project=p)
    tag_list = []
    modes = {}
    default = []
    for masterui in m:
        if masterui.active:
            mappings = UIMapping.objects.filter(master_ui=masterui, active=True)
            for mapping in mappings:
                if mapping.default:
                    default.append(mapping.tag.id)
    return default


#import operator

#search_fields = ('title', 'body', 'summary')
#q_objects = [Q(**{field + '__icontains':q}) for field in search_fields]
#queryset = BlogPost.objects.filter(reduce(operator.or_, q_objects))


def filter_recs_for_tags(p, tagids_from_request, l):
    logging.debug("filter_recs_for_tags enter")
    recs = []
    tags_from_request = Tag.objects.filter(id__in=tagids_from_request)

    tags_per_cat_dict = {}
    cats = TagCategory.objects.all()
    for cat in cats:
        tags_per_cat_dict[cat] = Tag.objects.filter(tag_category=cat)

    project_recs = Asset.objects.filter(project=p, submitted=True, audiolength__gt=1000, language=l).distinct()
    for rec in project_recs:
        remove = False
        for cat in cats:
            if remove:
                break
            #tags_per_category = Tag.objects.filter(tag_category=cat)
            tags_per_category = tags_per_cat_dict[cat]
            tags_for_this_cat_from_request = filter(lambda x: x in tags_per_category, tags_from_request)
            tags_for_this_cat_from_rec = filter(lambda x: x in tags_per_category, rec.tags.all())
            # if the asset has any tags from this category, make sure at least one match with exists, else remove
            if len(tags_for_this_cat_from_request) > 0:
                found = False
                if len(tags_for_this_cat_from_rec) > 0 and len(tags_for_this_cat_from_request) > 0:
                    for t in tags_for_this_cat_from_request:
                        if t in tags_for_this_cat_from_rec:
                            found = True
                            break
                if not found:
                    remove = True
        if not remove:
            recs.append(rec)

    return recs
# form args:
#event_type <string>
#session_id <integer>
#[client_time] <string using RFC822 format>
#[latitude] <float?>
#[longitude] <float?>
#[tags] (could possibly be incorporated into the 'data' field?)
#[data]


def log_event(event_type, session_id, form):
    s = Session.objects.get(id=session_id)
    if s == None:
        raise roundexception.RoundException("failed to access session " + str(session_id));
    client_time = None
    latitude = None
    longitude = None
    tags = None
    data = None
    if form != None:
        if form.has_key("client_time"):
            client_time = form["client_time"]
        if form.has_key("latitude"):
            latitude = form["latitude"]
        if form.has_key("longitude"):
            longitude = form["longitude"]
        if form.has_key("tags"):
            tags = form["tags"]
        if form.has_key("data"):
            data = form["data"]

    e = Event(session=s,
              event_type=event_type,
              server_time=datetime.datetime.now(),
              client_time=client_time,
              latitude=latitude,
              longitude=longitude,
              tags=tags,
              data=data)
    e.save()

    return True


def add_asset_to_session_history_and_update_metadata(asset_id, session_id, duration):
    logging.debug("!!!!add_recording_to_session_history called with recording " + str(asset_id) + " session_id: " + str(session_id) + " duration: " + str(int(duration)))
    admin = icecast2.Admin(settings.config["icecast_host"] + ":" + str(settings.config["icecast_port"]),
                           settings.config["icecast_username"],
                           settings.config["icecast_password"])
    logging.debug("add_asset_to_session_history_and_update_metadata: got admin")
    admin.update_metadata(asset_id, session_id)
    logging.debug("add_asset_to_session_history_and_update_metadata: returned!")

    #c = pycurl.Curl()
    #c.setopt(pycurl.USERPWD, "admin:roundice")
    #logging.debug("add_asset_to_session_history_and_update_metadata - enter")
    #sysString = "http://" + settings.config["icecast_host"] + ":" + str(settings.config["icecast_port"])  + "/admin/metadata.xsl?mount=/stream" + str(session_id) + ".mp3&mode=updinfo&charset=UTF-8&song=assetid" + str(asset.id)
    #logging.debug("add_asset_to_session_history_and_update_metadataa - sysString: "+ sysString)
    #c.setopt(pycurl.URL, sysString)
    #c.perform()
    s = Session.objects.get(id=session_id)
    ass = Asset.objects.get(id=asset_id)
    try:
        hist = ListeningHistoryItem(session=s, asset=ass, starttime=datetime.datetime.now(), duration=int(duration))
        hist.save()
    except:
        logging.debug("failed to save listening history!")
    return True


def cleanup_history_for_session(session_id):
    ListeningHistoryItem.objects.filter(session=session_id).delete()


def get_current_streaming_asset(session_id):
    l = ListeningHistoryItem.objects.filter(session=session_id).order_by('-starttime')[0]
    return l


def get_asset(asset_id):
    return Asset.objects.get(id=asset_id)
