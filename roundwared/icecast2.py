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
import libxml2
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class Admin:

    def __init__(self):
        self.auth = (str(settings.ICECAST_USERNAME), str(settings.ICECAST_PASSWORD))
        self.base_uri = "http://" + settings.ICECAST_HOST + ":" + settings.ICECAST_PORT

    def get_mount_list(self):
        result = self.process_xml(
            "/admin/listmounts", "//icestats/source/@mount")
        if result:
            return result
        else:
            return []

    def get_client_count(self, mount):
        result = self.process_xml(
            "/admin/listclients?mount=" + mount,
            "//icestats/source/Listeners")
        if result:
            return int(result[0])
        else:
            return 0

    def stream_exists(self, mount):
        for m in self.get_mount_list():
            if m == mount:
                return True
        return False

    def process_xml(self, url, xpath):
        # logger.debug("Request: %s, auth=%s", self.base_uri + url, self.auth)
        response = requests.get(self.base_uri + url, auth=self.auth)
        response.raise_for_status()
        # logger.debug("Response: %s", response.content)
        # Parse the XML and get the requested xpath results.
        xml = libxml2.parseDoc(response.content)
        context = xml.xpathNewContext()
        results = map(lambda x: x.content, context.xpathEval(xpath))
        # Must get the complete results before running freeDoc()
        xml.freeDoc()
        return results

    def update_metadata(self, asset_id, session_id):
        url = "/admin/metadata"
        uri = self.base_uri + url + "?mount=/stream" + str(session_id) + \
            ".mp3&mode=updinfo&charset=UTF-8&song=assetid" + str(asset_id)

        # TODO requests.get params value should be used instead of building
        # the GET value list manually, but the Requests library URL encodes
        # the values and Icecast does not accept that. Tested with Icecast
        # 2.3.2 (Ubuntu 12.04 repo version) and 2.4.0 (current compiled.)
        # Bug report filed against Icecast: https://trac.xiph.org/ticket/2031
        logger.debug("Request: %s, auth=%s", uri, self.auth)
        response = requests.get(uri, auth=self.auth)
        logger.debug(response.url)
        response.raise_for_status()
        logger.debug("Response: %s", response.content)
