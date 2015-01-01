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
except ImportError: # pragma: no cover
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
        self.playlist = []
        # A list of nearby played assets. We don't want to repeat nearby assets
        # even if they are removed from the ban list(dict.)
        self.banned_proximity = []
        # A dict of temporarily banned_timeout assets, key is asset.id and value is
        # timestamp of last play time. Reset only when stream is restarted.
        self.banned_timeout = {}
        self.lock = threading.Lock()
        self.update_request(self.request, update_nearby=False)

    def update_request(self, request, update_nearby=True, lock=True):
        """
        Updates/Initializes the request stored in the collection by filling
        all with assets filtered by tags. Optionally leaves
        playlist empty so no assets are triggered until
        modify_stream or move_listener are called.
        Lock is disabled when called by get_recording().
        """
        if lock:
            self.lock.acquire()

        tags = request.get("tags", None)
        self.all = db.get_recordings(request["session_id"], tags)
        # Updating nearby_recording will start stream audio asset play back.
        if update_nearby:
            self._update_nearby(request)
        logger.debug("Asset Counts - all: %s, playlist: %s, banned_proximity: %s, banned_timeout: %s." %
                     (len(self.all),
                      self.count(),
                      len(self.banned_proximity),
                      len(self.banned_timeout),
                      ))
        if lock:
            self.lock.release()

    # Gets a new recording to play.
    # @profile(stats=True)
    def get_recording(self):
        self.lock.acquire()
        recording = None
        logger.debug("We have %s playlist recordings.",
                     self.count())

        # If there are no playlist assets, but there are available played.
        if not self.has_nearby_unplayed() and self.has_played():
            p = models.Project.objects.get(id=int(self.request['project_id']))
            # Check if continuous is enabled for the project.
            if p.is_continuous():
                logger.debug("Playback mode: continuous")
                # Clear the ban list
                self.banned_timeout = {}
                # Clear the nearby played list
                self.banned_proximity = []
                # Update the list of playlist.
                self.update_request(self.request, update_nearby=True,
                                    lock=False)

        # If there are now any recordings available, get one.
        if self.has_nearby_unplayed():
            recording = self.playlist.pop()

        # If a recording was found.
        if recording:
            logger.debug("Found %s", recording.filename)
            # Add the recording to the ban list.
            self.banned_timeout[recording.id] = time()
            # Add the recording to the nearby played list.
            self.banned_proximity.append(recording)
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
        self.playlist.append(a)
        self.lock.release()

    # Updates the collection of recordings according to a new listener
    # position.
    def move_listener(self, listener):
        self.lock.acquire()
        self._update_nearby(listener)
        self.lock.release()

    # A list of string so of the filenames of the recordings. Useful
    # debugging log messages.
    def get_filenames(self):
        return map(
            lambda recording: recording.filename,
            self.playlist)

    def has_nearby_unplayed(self):
        """
        Returns true if there are any recordings left to play.
        """
        return len(self.playlist) > 0

    def count(self):
        return len(self.playlist)

    def has_played(self):
        """
        Returns true if there are banned_timeout or banned_proximity recordings.
        """
        return (len(self.banned_proximity) > 0 and len(self.banned_timeout) > 0)

    # Private
    def _update_nearby(self, listener):
        current_time = time()
        # Remove all expired asset bans from the ban list.
        self.banned_timeout = {id:lastplay for id, lastplay in self.banned_timeout.iteritems()
                       if (lastplay + settings.BANNED_TIMEOUT_LIMIT) > current_time}
        # Remove no longer nearby items from the nearby played list.
        self.banned_proximity = [r for r in self.banned_proximity
                              if self._is_nearby(listener, r)]
        # If debug, print some nice details.
        if settings.DEBUG:
            time_remaining = {}
            for id, lastplay in self.banned_timeout.iteritems():
                time_remaining[id] = int((lastplay +
                    settings.BANNED_TIMEOUT_LIMIT) - current_time)

            logger.debug("Timeout banned assets and seconds remaining: %s" %
                         time_remaining)
            logger.debug("Proximity banned assets: %s" %
                         self.banned_proximity)

        self.playlist = []
        for r in self.all:
            # If the asset is nearby, not nearby banned_timeout and not timeout banned_timeout,
            # then add it to the list of playlist items.
            if (r.id not in self.banned_timeout and
                    r not in self.banned_proximity and
                    self._is_nearby(listener, r)):
                self.playlist.append(r)

        logger.debug('Ordering is: ' + self.ordering)
        if self.ordering == 'random':
            self.playlist = order_assets_randomly(self.playlist)
        elif self.ordering == 'by_like':
            self.playlist = order_assets_by_like(self.playlist)
        elif self.ordering == 'by_weight':
            self.playlist = order_assets_by_weight(self.playlist)


    # Private
    def _is_nearby(self, listener, recording):
        """
        True if the listener and recording are close enough to be heard.
        """
        if 'latitude' in listener and 'longitude' in listener:
            distance = gpsmixer.distance_in_meters(
                listener['latitude'], listener['longitude'],
                recording.latitude, recording.longitude)

            return distance <= self.radius
        else:
            return True
