# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
import logging
import datetime
from django.templatetags.i18n import language
try:
    from profiling import profile
except ImportError:
    pass
from django.conf import settings
from roundware.lib.exception import RoundException
from roundware.rw.models import Session
from roundware.rw.models import Language
from roundware.rw.models import Event
from roundware.rw.models import Asset
from roundware.rw.models import Tag
from roundware.rw.models import MasterUI
from roundware.rw.models import UIMapping
from roundware.rw.models import ListeningHistoryItem
from roundwared import icecast2
from cache_utils.decorators import cached
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

# @profile(stats=True)
def get_config_tag_json(p=None, s=None):
    if s is None and p is None:
        raise RoundException("Must pass either a project or "
                                            "a session")
    language = Language.objects.filter(language_code='en')[0]
    if s is not None:
        p = s.project
        language = s.language

    m = MasterUI.objects.filter(project=p)
    modes = {}

    for masterui in m:
        if masterui.active:
            mappings = UIMapping.objects.filter(
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


# @profile(stats=True)
@cached(30)
def get_recordings(session_id, tags=None):

    # If the session_is is a list, get the first value
    # TODO: Remove check for a session_id list.
    # session_id is a list at stream.modify_stream() in roundwared.rounddbus.add_stream_signal_receiver()
    # session_id is a list before it is sent out on dbus in roundware.rw.views.main()
    if isinstance(session_id, list):
        session_id = session_id[0]

    logger.debug("Got session_id: %s", session_id)
    session = Session.objects.select_related('project',
                                           'language').get(id=session_id)
    project = session.project

    tag_list = None
    if tags:
        if isinstance(tags, list):
            tag_list = tags
        else:
            # Assuming string, make an int list from the "string,string,string"
            tag_list = map(int, tags.split(","))
    else:
        tag_list = get_default_tags_for_project(project)
        logger.debug("Using project default tags")

    recordings = []
    if tag_list:
        recordings = filter_recs_for_tags(project, tag_list, session.language)

    logger.debug("Found %s recordings for project %s",
                 len(recordings), project.name)
    return recordings


# @profile(stats=True)
def get_default_tags_for_project(project):
    m = MasterUI.objects.filter(project=project, active=True)
    default = []
    for masterui in m:
        mappings = UIMapping.objects.filter(master_ui=masterui,
                                            active=True, default=True)
        for mapping in mappings:
            default.append(mapping.tag.id)
    return default


# @profile(stats=True)
@cached(60 * 1)
def filter_recs_for_tags(p, tagids_from_request, l):
    """
    Return Assets containing at least one matching tag in _each_ available
    tag category with the tags supplied in tagids_from_request.
    i.e., an Asset, to be returned, must match at least one tag from each
    category.  It won't be returned if it has a tag from one tagcategory
    but not another.
    """
    # TODO: This function can be replaced with SQL.
    logger.debug("Tags: %s", tagids_from_request)

    recs = []
    tag_ids_per_cat_dict = {}

    project_cats = p.get_tag_cats_by_ui_mode(settings.LISTEN_UIMODE)
    logger.debug("Project tag categories: %s", project_cats)
    for cat in project_cats:
        # for each tag category a list of all of the tags with that cat
        tag_ids_per_cat_dict[cat.id] = [
            tag.id for tag in Tag.objects.filter(tag_category=cat)]
    # Note the audiolength must be greater than 1000 to be returned.
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
    s = Session.objects.get(id=session_id)
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

    e = Event(session=s,
              event_type=event_type,
              server_time=datetime.datetime.now(),
              client_time=client_time,
              latitude=latitude,
              longitude=longitude,
              tags=tags,
              data=data)
    e.save()

def add_asset_to_session_history_and_update_metadata(asset_id, session_id, duration):
    logger.debug("Called with recording " +
                 str(asset_id) + " session_id: " + str(session_id) + " duration: " + str(int(duration)))
    admin = icecast2.Admin()
    admin.update_metadata(asset_id, session_id)

    s = Session.objects.get(id=session_id)
    asset = Asset.objects.get(id=asset_id)
    try:
        hist = ListeningHistoryItem(
            session=s, asset=asset, starttime=datetime.datetime.now(), duration=int(duration))
        hist.save()
    except:
        logger.warning("Failed to save listening history!")
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
