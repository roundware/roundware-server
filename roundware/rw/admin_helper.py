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


import logging
from django.conf import settings
from roundwared import server as rwapi

logger = logging.getLogger(__name__)

def create_envelope(instance, **kwargs):
    """
    Called before the Asset is saved.
    This function retrieves an envelope_id from the API server
    """
    instance.filename = instance.file.name
    session_id = getattr(settings, "DEFAULT_SESSION_ID", "-1")

    fake_request = FakeRWRequest()
    fake_request.GET = {'session_id': session_id}
    logger.debug(fake_request.GET)

    response = rwapi.create_envelope(fake_request)
    logger.debug(response)

    if 'error_message' in response:
        logger.error("error message is pre_save: %s" %
                     response['error_message'])
        return

    # get the envelope Id from the return message
    instance.envelope_id = response['envelope_id']


def add_asset_to_envelope(instance, **kwargs):

    fake_request = FakeRWRequest()
    fake_request.GET = {
        'envelope_id': instance.envelope_id,
        'asset_id': instance.id,
    }
    logger.debug(fake_request.GET)

    content = rwapi.add_asset_to_envelope(fake_request)
    logger.debug(content)
    if 'error_message' in content:
        logger.error("error message is post_save: %s" %
                    content['error_message'])
        return

class FakeRWRequest:
    """
    Fake HTTP GET request object to send the Roundware API server functions
    """
    GET = {}
