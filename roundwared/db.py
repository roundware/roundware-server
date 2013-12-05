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


import logging
import datetime
try:
    from profiling import profile
except ImportError:
    pass
from roundwared import settings
from roundwared import roundexception
from roundware import settings as rw_settings
from roundware.rw.models import Session
from roundware.rw.models import Language
from roundware.rw.models import Event
from roundware.rw.models import Project
from roundware.rw.models import Asset
from roundware.rw.models import Tag
from roundware.rw.models import MasterUI
from roundware.rw.models import UIMapping
from roundware.rw.models import ListeningHistoryItem
from roundwared import icecast2
from cache_utils.decorators import cached


# @profile(stats=True)
def get_config_tag_json(p=None, s=None):
    if s is None and p is None:
        raise roundexception.RoundException("Must pass either a project or "
                                            "a session")
    lingo = Language.objects.filter(language_code='en')[0]
    if s is not None:
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


# @profile(stats=True)
@cached(30)
def get_recordings(request):

    logging.debug("get_recordings: got request: " + str(request))
    recs = []
    p = None
    s = None

    # TODO XXX: passing a project_id is actually useless in terms of this method
    # but get_recording will fail without one in the request.  This will always get
    # the project from the session, and fail if no session is passed.
    if request.has_key("project_id") and hasattr(request["project_id"], "__iter__") and len(request["project_id"]) > 0:
        logging.debug("get_recordings: got project_id: " + str(request["project_id"][0]))
        p = Project.objects.get(id=request["project_id"][0])
    elif request.has_key("project_id") and not hasattr(request["project_id"], "__iter__"):
        logging.debug("get_recordings: got project_id: " + str(request["project_id"]))
        p = Project.objects.get(id=request["project_id"])

    if request.has_key("session_id") and hasattr(request["session_id"], "__iter__") and len(request["session_id"]) > 0:
        logging.debug("get_recordings: got session_id: " + str(request["session_id"][0]))
        s = Session.objects.select_related('project', 'language').get(id=request["session_id"][0])
        p = s.project
    elif request.has_key("session_id") and not hasattr(request["session_id"], "__iter__"):
        logging.debug("get_recordings: got session_id: " + str(request["session_id"]))
        s = Session.objects.select_related('project', 'language').get(id=request["session_id"])
        p = s.project
    elif not request.has_key("session_id") or len(request["session_id"]) == 0:
        # must raise error if no session passed because it will otherwise error below
        # XXX TODO: or, fix this to match desired functionality
        raise roundexception.RoundException("get_recordings must be passed a session id")


    # this first check checks whether tags is a list of numbers.
    if request.has_key("tags") and hasattr(request["tags"], "__iter__") and len(request["tags"]) > 0:
        logging.debug("get_recordings: got " + str(len(request["tags"])) + "tags.")
        recs = filter_recs_for_tags(p, request["tags"], s.language)
    # this second check checks whether tags is a string representation of a list of numbers.
    elif request.has_key("tags") and not hasattr(request["tags"], "__iter__"):
        logging.debug("get_recordings: tags supplied: " + request["tags"])
        recs = filter_recs_for_tags(p, request["tags"].split(","), s.language)
    else:
        logging.debug("get_recordings: no tags supplied")
        if s != None:
            recs = filter_recs_for_tags(p, get_default_tags_for_project(p, s), s.language)

    logging.debug("db: get_recordings: got " + str(len(recs)) + " recordings from db for project " + str(p.id))
    return recs


# @profile(stats=True)
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

# @profile(stats=True)
@cached(60*1)
def filter_recs_for_tags(p, tagids_from_request, l):
    """ Return Assets containing at least one matching tag in _each_ available 
    tag category with the tags supplied in tagids_from_request.
    i.e., an Asset, to be returned, must match at least one tag from each 
    category.  It won't be returned if it has a tag from one tagcategory
    but not another.
    """
    logging.debug("filter_recs_for_tags enter")

    recs = []
    tag_ids_per_cat_dict = {}
    # project_cats = TagCategory.objects.filter()

    project_cats = p.get_tag_cats_by_ui_mode(rw_settings.LISTEN_UIMODE)
    for cat in project_cats:
        # for each tag category a list of all of the tags with that cat
        tag_ids_per_cat_dict[cat.id] = [tag.id for tag in Tag.objects.filter(tag_category=cat)]


    project_recs = Asset.objects.filter(project=p, submitted=True, audiolength__gt=1000, language=l).distinct()
    for rec in project_recs:
        remove = False
        # all tags for this asset
        rec_tag_ids = [tag.id for tag in rec.tags.all()]
        for cat in project_cats:
            if remove:
                # don't return this asset, stop looking through tagcats
                break
            # all of this tagcategory's tags
            tags_per_category = tag_ids_per_cat_dict[cat.id]
            # any tag ids passed in the request that are in this tagcategory
            tag_ids_for_this_cat_from_request = filter(lambda x: x in tags_per_category, tagids_from_request)

            # any tag ids of this asset that are in this tagcategory
            tag_ids_for_this_cat_from_asset = filter(lambda x: x in tags_per_category, rec_tag_ids)
            
            # if no tags passed in request are in this category, then 
            # look at next category. 

            # if any tags passed in request are in this category, then
            # make sure any asset returned has at least one tag in this category
            # e.g., pass tag id 1 in request.  if tag id 1 is in this category, then
            # any asset returned must have at least one tag for this category
            if len(tag_ids_for_this_cat_from_request) > 0:
                found = False
                # if this asset has any tags in this category, ...
                if len(tag_ids_for_this_cat_from_asset) > 0:
                    # then look through tags in this category from request...
                    for t in tag_ids_for_this_cat_from_request:
                        # for a tag on this asset
                        if t in tag_ids_for_this_cat_from_asset:
                            found = True
                            break
                if not found:
                    remove = True

        # if no tags passed in request are in any of the project categories,
        # return this asset.  or, if the asset does have a tag in this category,
        # return it.

        if not remove:
            recs.append(rec)
    logging.debug("\n\n\nfilter_recs_for_tags returned %s Assets \n\n\n" % (len(recs)))
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

    #import pycurl
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
    try:
        l = ListeningHistoryItem.objects.filter(session=session_id).order_by('-starttime')[0]
        return l
    except IndexError:
        return None

def get_asset(asset_id):
    return Asset.objects.get(id=asset_id)
