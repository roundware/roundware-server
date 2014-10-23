# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# MODES: True Shuffle, Random cycle N times

from __future__ import unicode_literals
import logging
import threading
import os.path
from time import time
try:
    from profiling import profile
except ImportError:
    pass

from django.conf import settings
from roundwared import gpsmixer
from roundware.rw import models
from roundwared import db
from roundwared.asset_sorters import order_assets_randomly, order_assets_by_like, order_assets_by_weight

logger = logging.getLogger(__name__)


class RecordingCollection:
    ######################################################################
    # Public
    ######################################################################

    def __init__(self, stream, request, radius, ordering='random'):
        logger.debug("RecordingCollection init - request: " + str(request))
        self.stream = stream
        self.request = request
        self.radius = radius
        self.ordering = ordering
        # these are lists of model.Recording objects ie [rec1,rec2,etc]
        self.all = []
        # The main list of assets to play, in reverse order because it is a stack.
        self.nearby_unplayed = []
        # A dict of temporarily banned assets, key is asset.id and value is
        # timestamp of last play time. Reset only when stream is restarted.
        self.banned = {}
        self.lock = threading.Lock()
        self.update_request(self.request, update_nearby=False)

    def update_request(self, request, update_nearby=True, lock=True):
        """
        Updates/Initializes the request stored in the collection by filling
        all with assets filtered by tags. Optionally leaves
        nearby_unplayed empty so no assets are triggered until
        modify_stream or move_listener are called.
        Lock is disabled when called by get_recording().
        """
        if lock:
            self.lock.acquire()

        tags = getattr(request, "tags", None)
        self.all = db.get_recordings(request["session_id"], tags)
        # Updating nearby_recording will start stream audio asset playback.
        if update_nearby:
            self.__update_nearby(request)
        logger.debug("Asset Counts - all: %s, nearby_unplayed: %s, banned: %s" %
                     (len(self.all),
                      len(self.nearby_unplayed),
                      len(self.banned)))
        if lock:
            self.lock.release()

    # Gets a new recording to play.
    # @profile(stats=True)
    def get_recording(self):
        logger.debug("Getting a recording.")
        self.lock.acquire()
        recording = None
        logger.debug("We have %s unplayed recordings.",
                     len(self.nearby_unplayed))

        # If there are any recordings banned and no unplayed recordings
        if len(self.banned) > 0 and not self.has_recordings():
            p = models.Project.objects.get(id=int(self.request['project_id']))
            # Check if continuous is disabled for the project.
            if not p.is_continuous():
                logger.debug("Stop mode")
                self.lock.release()
                return None
            logger.debug("Continuous mode")
            # Clear the ban list
            self.ban = {}
            # Update the list of nearby_unplayed.
            self.update_request(self.request, update_nearby=True, lock=False)

        # If there are now any recordings available, get one.
        if self.has_recordings():
            recording = self.nearby_unplayed.pop()

        # If a recording was found.
        if recording:
            logger.debug("Got %s", recording.filename)
            # Add the recording to the ban list.
            self.banned[recording.id] = time()
            if not settings.TESTING:
                filepath = os.path.join(settings.MEDIA_ROOT, recording.filename)
                # Check if the file exists on the server, not the stream crashes.
                if not os.path.isfile(filepath):
                    logger.error("File not found: %s", filepath)
                    recording = None

        self.lock.release()
        return recording

    def add_recording(self, asset_id):
        self.lock.acquire()
        logger.debug("asset id: %s " % asset_id)
        a = models.Asset.objects.get(id=str(asset_id))
        self.nearby_unplayed.append(a)
        self.lock.release()

    # Updates the collection of recordings according to a new listener
    # position.
    def move_listener(self, listener):
        self.lock.acquire()
        self.__update_nearby(listener)
        self.lock.release()

    # A list of string so of the filenames of the recordings. Useful
    # debugging log messages.
    def get_filenames(self):
        return map(
            lambda recording: recording.filename,
            self.nearby_unplayed)

    # True if the collection has any recordings left to play.
    def has_recordings(self):
        return len(self.nearby_unplayed) > 0

    # Private
    def __update_nearby(self, listener):
        current_time = time()
        # Remove all expired asset bans from the ban list.
        self.banned = {id:lastplay for id, lastplay in self.banned.iteritems()
                       if (lastplay + settings.REPLAY_BAN_TIME_LIMIT) > current_time}
        logger.debug("Current timestamp: %d, banned assets and last play: %s" %
                     (current_time, self.banned))

        # Clear the list of nearby_unplayed assets.
        self.nearby_unplayed = []
        # Check all assets.
        for r in self.all:
            # If asset is banned, skip it.
            if r.id in self.banned:
                continue
            # If the asset is nearby add it to the list of unplayed
            if self.__is_nearby(listener, r):
                self.nearby_unplayed.append(r)

        logger.debug('Ordering is: ' + self.ordering)
        if self.ordering == 'random':
            self.nearby_unplayed = order_assets_randomly(self.nearby_unplayed)
        elif self.ordering == 'by_like':
            self.nearby_unplayed = order_assets_by_like(self.nearby_unplayed)
        elif self.ordering == 'by_weight':
            self.nearby_unplayed = order_assets_by_weight(self.nearby_unplayed)


    # Private
    def __is_nearby(self, listener, recording):
        """
        True if the listener and recording are close enough to be heard.
        """
        if 'latitude' in listener and listener['latitude'] \
                and listener['longitude']:
            distance = gpsmixer.distance_in_meters(
                listener['latitude'], listener['longitude'],
                recording.latitude, recording.longitude)

            return distance <= self.radius
        else:
            return True
