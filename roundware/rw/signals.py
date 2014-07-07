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


import json
import logging
import urllib
import urllib2
from django.conf import settings

API_URL = getattr(settings, "API_URL")
logger = logging.getLogger(__name__)


def create_envelope(instance, **kwargs):
    """
    Called before the Asset is saved.
    This function retrieves an envelope_id from the API server
    """
    instance.filename = instance.file.name
    # build get string
    get_data = [('operation', 'create_envelope'),
                ('session_id', getattr(settings, "DEFAULT_SESSION_ID", "-1"))]     # a sequence of two element tuples

    # post to server
    result = urllib2.urlopen(API_URL + "?" + urllib.urlencode(get_data))
    # read response
    content = json.loads(result.read())

    if 'error_message' in content:
        logger.info("error message is pre_save: %s" % content['error_message'])
        return
        # get the envelope Id from the return message
    instance.ENVELOPE_ID = content['envelope_id']


def add_asset_to_envelope(instance, **kwargs):
    # build post string
    post_data = [('operation', 'add_asset_to_envelope'),
                 ('envelope_id', instance.ENVELOPE_ID),
                 ('asset_id', instance.id),
                 ]
    # post to server
    result = urllib2.urlopen(API_URL, urllib.urlencode(post_data))
    # read response
    content = json.loads(result.read())

    if 'error_message' in content:
        logger.info("error message is post_save: %s" %
                    content['error_message'])
        return
