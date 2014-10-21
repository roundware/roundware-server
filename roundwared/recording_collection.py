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
        self.far = []
        self.nearby_played = []
        # The main list of assets to play, in reverse order because it is a stack.
        self.nearby_unplayed = []
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
        self.far = self.all
        # Clear the nearby recordings storage.
        self.nearby_played = []
        self.nearby_unplayed = []
        # Updating nearby_recording will start stream audio asset playback.
        if update_nearby:
            self.update_nearby_recordings(request)
        logger.debug("all count: " + str(len(self.all))
                     + ", far count: " +
                     str(len(self.far))
                     + ", nearby_played count: " +
                     str(len(self.nearby_played))
                     + ", nearby_unplayed count: " + str(len(self.nearby_unplayed)))
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
        if self.has_recordings():
            recording = self.nearby_unplayed.pop()
            self.nearby_played.append(recording)

        elif len(self.nearby_played) > 0:
            p = models.Project.objects.get(id=int(self.request['project_id']))
            # Check project settings, if continuous is enabled.
            if not p.is_continuous():
                logger.debug("Stop mode")
                self.lock.release()
                return None
            logger.debug("Continuous mode")
            # Update the list of nearby_unplayed.
            self.update_request(self.request, update_nearby=True, lock=False)
            recording = self.nearby_unplayed.pop()
            self.nearby_played.append(recording)

        # If a recording was found and unit tests are not running.
        if recording and not settings.TESTING:
            logger.debug("Got %s", recording.filename)
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
        # logger.debug("move_listener")
        self.lock.acquire()
        self.update_nearby_recordings(listener)
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

    ######################################################################
    # Private
    ######################################################################

    def update_nearby_recordings(self, listener):
        new_far_recordings = []
        new_nearby_unplayed_recordings = []
        new_nearby_played_recordings = []

        for r in self.far:
            if self.is_nearby(listener, r):
                new_nearby_unplayed_recordings.append(r)
            else:
                new_far_recordings.append(r)

        for r in self.nearby_unplayed:
            if self.is_nearby(listener, r):
                new_nearby_unplayed_recordings.append(r)
            else:
                new_far_recordings.append(r)

        for r in self.nearby_played:
            if self.is_nearby(listener, r):
                new_nearby_played_recordings.append(r)
            else:
                new_far_recordings.append(r)

        logger.debug('Ordering is: ' + self.ordering)
        if self.ordering == 'random':
            new_nearby_unplayed_recordings = \
                order_assets_randomly(new_nearby_unplayed_recordings)
        elif self.ordering == 'by_like':
            new_nearby_unplayed_recordings = \
                order_assets_by_like(new_nearby_unplayed_recordings)
        elif self.ordering == 'by_weight':
            new_nearby_unplayed_recordings = \
                order_assets_by_weight(new_nearby_unplayed_recordings)

        self.far = new_far_recordings
        self.nearby_unplayed = new_nearby_unplayed_recordings
        self.nearby_played = new_nearby_played_recordings

    # True if the listener and recording are close enough to be heard.
    def is_nearby(self, listener, recording):
        if 'latitude' in listener and listener['latitude'] \
                and listener['longitude']:
            distance = gpsmixer.distance_in_meters(
                listener['latitude'], listener['longitude'],
                recording.latitude, recording.longitude)

            return distance <= self.radius
        else:
            return True
