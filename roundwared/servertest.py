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


import db
import json
#print(json.dumps(db.get_config_tag_json_for_project(1), indent=4))
#print(db.get_recordings({'project_id':1,'latitude':1, 'longitude':1, 'tags':[1,3,6]}))
#db.add_asset_to_session_history_and_update_metadata(1,1)


import string
import datetime
import time
from roundwared import settings
from roundwared import gpsmixer
from roundwared import roundexception
from django.db.models import Q
from roundware.rw.models import Session
from roundware.rw.models import Event
from roundware.rw.models import Project
from roundware.rw.models import Asset
from roundware.rw.models import Tag
from roundware.rw.models import TagCategory
from roundware.rw.models import MasterUI
from roundware.rw.models import UIMapping
from roundware.rw.models import ListeningHistoryItem
from roundware.rw.models import LocalizedString
from roundware.rw.models import Language
from roundwared import icecast2
import operator
import pycurl

#l1 = Language(language_code = 'en')
#l1.save()

#l2 = Language(language_code = 'es')
#l2.save()

#request = {'latitude': False, 'project_id': 1, 'longitude': False}
#db.get_recordings(request)
p = Project.objects.get(id=1)
s = Session.objects.get(id=2210)
db.get_default_tags_for_project(p, s)


def migrate_tag_and_project_msgs():
    l = Language.objects.filter(language_code='en')[0]
    l_es = Language.objects.filter(language_code='es')[0]
    t = Tag.objects.all()
    for tag in t:
        ls = LocalizedString(language=l, localized_string=tag.value)
        ls.save()
        ls_es = LocalizedString(language=l_es, localized_string="spanish placeholder for: " + tag.value)
        ls_es.save()
        tag.loc_msg.add(ls)
        tag.loc_msg.add(ls_es)
        tag.description = tag.value
        tag.value = ""
        tag.save()

    p = Project.objects.all()
    for proj in p:
        if proj.sharing_message != None and proj.sharing_message != "":
            ls_share = LocalizedString(language=l, localized_string=proj.sharing_message)
            ls_share.save()
            ls_es = LocalizedString(language=l_es, localized_string="spanish placeholder for: " + proj.sharing_message)
            ls_es.save()
            proj.sharing_message_loc.add(ls_share)
            proj.sharing_message_loc.add(ls_es)
            proj.sharing_message = ""
            proj.save()
        if proj.out_of_range_message != None and proj.out_of_range_message != "":
            ls_range = LocalizedString(language=l, localized_string=proj.out_of_range_message)
            ls_range.save()
            ls_es = LocalizedString(language=l_es, localized_string="spanish placeholder for: " + proj.out_of_range_message)
            ls_es.save()
            proj.out_of_range_message_loc.add(ls_range)
            proj.out_of_range_message_loc.add(ls_es)
            proj.out_of_range_message = ""
            proj.save()

#migrate_tag_and_project_msgs()


def localize_all_assets_to_en():
    l = Language.objects.filter(language_code='en')[0]
    a = Asset.objects.all()
    for asset in a:
        asset.language = l
        asset.save()
