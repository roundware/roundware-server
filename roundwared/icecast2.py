# Roundware Server is released under the GNU Affero General Public License v3.
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
