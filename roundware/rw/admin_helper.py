# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
import logging
from django.conf import settings
from roundware.api1 import commands
from roundware.lib import api

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

    response = api.create_envelope(fake_request)
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

    content = api.add_asset_to_envelope(fake_request)
    logger.debug(content)
    if 'error_message' in content:
        logger.error("error message is post_save: %s" % content['error_message'])
        return


class FakeRWRequest:
    """
    Fake HTTP GET request object to send the Roundware API server functions
    """
    GET = {}
