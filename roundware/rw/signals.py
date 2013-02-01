import json
import logging
import urllib
import urllib2
from django.conf import settings

API_URL = getattr(settings, "API_URL")

logger = logging.getLogger(name=__file__)

def create_envelope(instance, **kwargs):
    """
    Called before the Asset is saved.
    This function retrieves an envelope_id from the API server
    """
    instance.filename = instance.file.name
    #build get string
    get_data = [('operation','create_envelope'),
                ('session_id', getattr(settings, "DEFAULT_SESSION_ID", "-1"))]     # a sequence of two element tuples

    #post to server
    result = urllib2.urlopen(API_URL + "?" + urllib.urlencode(get_data))
    #read response
    content = json.loads(result.read())

    if 'error_message' in content:
        logger.info("error message is pre_save: %s" % content['error_message'])
        return
        #get the envelope Id from the return message
    instance.ENVELOPE_ID = content['envelope_id']

def add_asset_to_envelope(instance, **kwargs):
    #build post string
    post_data = [('operation', 'add_asset_to_envelope'),
                 ('envelope_id', instance.ENVELOPE_ID),
                 ('asset_id', instance.id),
                 ('client_time', instance.audiolength),
                 ]
    #post to server
    result = urllib2.urlopen(API_URL, urllib.urlencode(post_data))
    #read response
    content = json.loads(result.read())

    if 'error_message' in content:
        logger.info("error message is post_save: %s" % content['error_message'])
        return