# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
import libxml2
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def mount_point(sessionid, audio_format):
    return '/stream%s.%s' % (sessionid, audio_format.lower())

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
        response.raise_for_status()
        logger.debug("Response: %s", response.content)
