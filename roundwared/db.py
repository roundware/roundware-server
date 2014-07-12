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
# along with this program.  If not, see
# <http://www.gnu.org/licenses/lgpl.html>.

#***********************************************************************************#


from __future__ import unicode_literals
import logging
import datetime
try:
    from profiling import profile
except ImportError:
    pass
from django.conf import settings
from roundwared import roundexception
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
logger = logging.getLogger(__name__)

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
    modes = {}

    for masterui in m:
        if masterui.active:
            mappings = UIMapping.objects.filter(
                master_ui=masterui, active=True)
            if masterui.header_text_loc.all():
                ht = masterui.header_text_loc.filter(
                    language=lingo)[0].localized_string
            else:
                ht = ""
            #masterD = masterui.toTagDictionary()
            masterD = {'name': masterui.name, 'header_text': ht, 'code': masterui.tag_category.name,
                       'select': masterui.select.name, 'order': masterui.index}
            masterOptionsList = []

            default = []
            for mapping in mappings:
                temp_desc = ""
                loc_desc = ""
                temp_desc = mapping.tag.loc_description.filter(language=lingo)
                if temp_desc:
                    loc_desc = temp_desc[0].localized_string
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
                                          'value': mapping.tag.loc_msg.filter(language=lingo)[0].localized_string})
            masterD["options"] = masterOptionsList
            masterD["defaults"] = default
            if masterui.ui_mode.name not in modes:
                modes[masterui.ui_mode.name] = [masterD, ]
            else:
                modes[masterui.ui_mode.name].append(masterD)

    return modes


# @profile(stats=True)
@cached(30)
def get_recordings(session_id, tags=None):
    logger.debug("Got session_id: %s", session_id)
    session = Session.objects.select_related('project',
                                           'language').get(id=session_id)
    project = session.project

    tag_list = None
    if tags:
        if isinstance(tags, list):
            tag_list = tags
        else:
            tag_list = tags.split(",")
    else:
        tag_list = get_default_tags_for_project(project, session)
        logger.debug("Using project default tags")

    recordings = []
    if tag_list:
        logger.debug("Tags supplied: %s", tag_list)
        recordings = filter_recs_for_tags(project, tag_list, session.language)
    else:
        logger.debug("No recordings available")

    logger.debug("Got %s recordings for project %s",
                 len(recordings), project.id)
    return recordings


# @profile(stats=True)
def get_default_tags_for_project(p, s):
    m = MasterUI.objects.filter(project=p)
    default = []
    for masterui in m:
        if masterui.active:
            mappings = UIMapping.objects.filter(
                master_ui=masterui, active=True)
            for mapping in mappings:
                if mapping.default:
                    default.append(mapping.tag.id)
    return default


#import operator

#search_fields = ('title', 'body', 'summary')
#q_objects = [Q(**{field + '__icontains':q}) for field in search_fields]
#queryset = BlogPost.objects.filter(reduce(operator.or_, q_objects))

# @profile(stats=True)
@cached(60 * 1)
def filter_recs_for_tags(p, tagids_from_request, l):
    """ Return Assets containing at least one matching tag in _each_ available
    tag category with the tags supplied in tagids_from_request.
    i.e., an Asset, to be returned, must match at least one tag from each
    category.  It won't be returned if it has a tag from one tagcategory
    but not another.
    """
    logger.debug("filter_recs_for_tags. Tags: %s", tagids_from_request)

    recs = []
    tag_ids_per_cat_dict = {}
    # project_cats = TagCategory.objects.filter()

    project_cats = p.get_tag_cats_by_ui_mode(settings.LISTEN_UIMODE)
    for cat in project_cats:
        # for each tag category a list of all of the tags with that cat
        tag_ids_per_cat_dict[cat.id] = [
            tag.id for tag in Tag.objects.filter(tag_category=cat)]

    project_recs = list(Asset.objects.filter(
        project=p, submitted=True, audiolength__gt=1000, language=l).distinct())
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
            tag_ids_for_this_cat_from_request = filter(
                lambda x: x in tags_per_category, tagids_from_request)

            # any tag ids of this asset that are in this tagcategory
            tag_ids_for_this_cat_from_asset = filter(
                lambda x: x in tags_per_category, rec_tag_ids)

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
    logger.debug(
        "filter_recs_for_tags returned %s Assets" % (len(recs)))
    return recs
# form args:
# event_type <string>
# session_id <integer>
#[client_time] <string using RFC822 format>
#[latitude] <float?>
#[longitude] <float?>
#[tags] (could possibly be incorporated into the 'data' field?)
#[data]


def log_event(event_type, session_id, form):
    s = Session.objects.get(id=session_id)
    if s == None:
        raise roundexception.RoundException(
            "failed to access session " + str(session_id))
    client_time = None
    latitude = None
    longitude = None
    tags = None
    data = None
    if form != None:
        if "client_time" in form:
            client_time = form["client_time"]
        if "latitude" in form:
            latitude = form["latitude"]
        if "longitude" in form:
            longitude = form["longitude"]
        if "tags" in form:
            tags = form["tags"]
        if "data" in form:
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
    logger.debug("add_recording_to_session_history called with recording " +
                 str(asset_id) + " session_id: " + str(session_id) + " duration: " + str(int(duration)))
    admin = icecast2.Admin(settings.ICECAST_HOST + ":" + str(settings.ICECAST_PORT),
                           settings.ICECAST_USERNAME,
                           settings.ICECAST_PASSWORD)
    logger.debug("add_asset_to_session_history_and_update_metadata: got admin")
    admin.update_metadata(asset_id, session_id)
    logger.debug("add_asset_to_session_history_and_update_metadata: returned")

    #import pycurl
    #c = pycurl.Curl()
    #c.setopt(pycurl.USERPWD, "admin:roundice")
    # logger.debug("add_asset_to_session_history_and_update_metadata - enter")
    #sysString = "http://" + settings.config["icecast_host"] + ":" + str(settings.config["icecast_port"])  + "/admin/metadata.xsl?mount=/stream" + str(session_id) + ".mp3&mode=updinfo&charset=UTF-8&song=assetid" + str(asset.id)
    # logger.debug("add_asset_to_session_history_and_update_metadataa - sysString: "+ sysString)
    #c.setopt(pycurl.URL, sysString)
    # c.perform()
    s = Session.objects.get(id=session_id)
    ass = Asset.objects.get(id=asset_id)
    try:
        hist = ListeningHistoryItem(
            session=s, asset=ass, starttime=datetime.datetime.now(), duration=int(duration))
        hist.save()
    except:
        logger.debug("failed to save listening history!")
    return True


def cleanup_history_for_session(session_id):
    ListeningHistoryItem.objects.filter(session=session_id).delete()


def get_current_streaming_asset(session_id):
    try:
        l = ListeningHistoryItem.objects.filter(
            session=session_id).order_by('-starttime')[0]
        return l
    except IndexError:
        return None


def get_asset(asset_id):
    return Asset.objects.get(id=asset_id)
