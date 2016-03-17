# Roundware Server is released under the GNU Affero General Public License v3.
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
from roundware.rw.models import Asset, Project, TimedAsset
from roundwared import db
from roundwared.asset_sorters import order_assets_randomly, order_assets_by_like, order_assets_by_weight

logger = logging.getLogger(__name__)


class RecordingCollection:
    ######################################################################
    # Public
    ######################################################################

    def __init__(self, stream, request, radius, ordering='random'):
        logger.debug("RecordingCollection init - request: " + str(request))
        # Start time is not valid until self.start() is called.
        self.start_time = 0
        self.stream = stream
        self.request = request
        self.radius = radius
        self.ordering = ordering
        self.project = Project.objects.get(id=int(self.request['project_id']))

        # these are lists of model.Recording objects ie [rec1,rec2,etc]
        self.all = []
        # The main list of assets to play, in reverse order because it is a stack.
        self.playlist_proximity = []
        # A list of nearby played assets. We don't want to repeat nearby assets
        # even if they are removed from the ban list(dict.)
        self.banned_proximity = []
        # A dict of temporarily banned_timeout assets, key is asset.id and value is
        # timestamp of last play time. Reset only when stream is restarted.
        self.banned_timeout = {}
        # A stack of assets from the project's TimedAssets
        self.playlist_timed = []

        self.lock = threading.Lock()
        self.update_request(self.request, update_proximity=False)
        # If geolisten is not enabled update the "proximity" playlist
        # @todo: Re-architect this.
        if not self.project.geo_listen_enabled:
            self._update_playlist_proximity(self.request)


    def start(self):
        """
        Init the timer with the actual audiotrack start time.
        """
        self.start_time = time()

    def update_request(self, request, update_proximity=True, lock=True):
        """
        Updates/Initializes the request stored in the collection by filling
        all with assets filtered by tags. Optionally leaves
        playlist_proximity empty so no assets are triggered until
        modify_stream or move_listener are called.
        Lock is disabled when called by get_recording().
        """
        if lock:
            self.lock.acquire()

        # Store the request details
        self.request = request
        tags = request.get("tags", None)
        self.all = db.get_recordings(request["session_id"], tags)
        # Updating nearby_recording will start stream audio asset play back.
        if update_proximity:
            self._update_playlist_proximity(request)
        logger.debug("Asset Counts - all: %s, playlist_proximity: %s, banned_proximity: %s, banned_timeout: %s." %
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
        """
        Gets a recording, bans it from repeating quickly and returns it.
        """
        self.lock.acquire()
        recording = self._get_recording()

        if recording:
            logger.debug("Found %s", recording.filename)
            # Add the recording to the ban list.
            self.banned_timeout[recording.id] = time()
            if self.project.geo_listen_enabled:
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

    def _get_recording(self):
        """
        Returns an item from the timed playlist if any exist, return a
        an item from the proximity playlist if any exist, otherwise return None
        """
        # prioritize timed-assets before proximity assets
        if self.project.timed_asset_priority:
            self._update_playlist_timed()
            if len(self.playlist_timed) > 0:
                return self.playlist_timed.pop()

        # If there are no playlist_proximity assets available, but there are
        # played assets available.
        if len(self.playlist_proximity) == 0 and self.has_played():
            # Check if continuous is enabled for the project.
            if (self.project.repeat_mode == Project.CONTINUOUS):
                logger.debug("Playback mode: continuous")
                # Clear the ban list
                self.banned_timeout = {}
                # Clear the nearby played list
                self.banned_proximity = []
                # Update the list of playlist_proximity.
                self._update_playlist_proximity(self.request)

        # If there are now any recordings available, get one.
        if len(self.playlist_proximity) > 0:
            return self.playlist_proximity.pop()

        # prioritize timed-assets after proximity assets
        if not self.project.timed_asset_priority:
            self._update_playlist_timed()
            if len(self.playlist_timed) > 0:
                return self.playlist_timed.pop()

        return None

    def add_recording(self, asset_id):
        self.lock.acquire()
        logger.debug("asset id: %s " % asset_id)
        a = Asset.objects.get(id=str(asset_id))
        self.playlist_proximity.append(a)
        self.lock.release()

    # Updates the collection of recordings according to a new listener
    # position.
    def move_listener(self, request):
        self.lock.acquire()
        self._update_playlist_proximity(request)
        self.lock.release()

    # A list of strings of the filenames of the recordings. Useful
    # debugging log messages.
    def get_filenames(self):
        return map(
            lambda recording: recording.filename,
            self.playlist_proximity)

    def count(self):
        return len(self.playlist_proximity) + len(self.playlist_timed)

    def has_played(self):
        """
        Returns true if there are banned_timeout or banned_proximity recordings.
        """
        return (len(self.banned_proximity) > 0 and len(self.banned_timeout) > 0)

    def order_assets(self, assets):
        """
        Order assets by ordering method set in project config
        """
        logger.debug("Ordering assets by: %s" % self.ordering)
        if self.ordering == 'random':
            return order_assets_randomly(assets)
        elif self.ordering == 'by_like':
            return order_assets_by_like(assets)
        elif self.ordering == 'by_weight':
            return order_assets_by_weight(assets)
        return []

    def _update_playlist_proximity(self, request):
        current_time = time()
        # Remove all expired asset bans from the ban list.
        self.banned_timeout = {id:lastplay for id, lastplay in self.banned_timeout.iteritems()
                       if (lastplay + settings.BANNED_TIMEOUT_LIMIT) > current_time}
        if self.project.geo_listen_enabled:
            # Remove no longer nearby items from the nearby played list.
            self.banned_proximity = [r for r in self.banned_proximity
                                  if self._is_nearby(request, r)]
        # If debug, print some nice details.
        if settings.DEBUG:
            time_remaining = {}
            for id, lastplay in self.banned_timeout.iteritems():
                time_remaining[id] = int((lastplay +
                    settings.BANNED_TIMEOUT_LIMIT) - current_time)

            logger.debug("Timeout banned assets and seconds remaining: %s" %
                         time_remaining)
            if self.project.geo_listen_enabled:
                logger.debug("Proximity banned assets: %s" %
                             self.banned_proximity)

        self.playlist_proximity = []
        for r in self.all:
            # If the asset is nearby, not nearby banned_timeout and not timeout banned_timeout,
            # then add it to the list of playlist_proximity items.
            if not self._banned(r) and self._is_nearby(request, r):
                self.playlist_proximity.append(r)

        # apply project ordering
        self.playlist_proximity = self.order_assets(self.playlist_proximity)


    def _is_nearby(self, request, recording):
        """
        True if the request and recording are close enough to be heard.
        """
        if not self.project.geo_listen_enabled:
            return True

        if 'latitude' in request and 'longitude' in request:
            distance = gpsmixer.distance_in_meters(
                request['latitude'], request['longitude'],
                recording.latitude, recording.longitude)

            return distance <= self.radius
        else:
            return True


    def _banned(self, recording):
        """
        Returns whether an asset/recording is currently banned.
        """

        return (recording.id in self.banned_timeout.keys() or
            recording in self.banned_proximity)

    def _update_playlist_timed(self):
        elapsed_time = time() - self.start_time
        # logger.debug("Elapsed Time: %s" % elapsed_time)

        # Get assets: End time > Elapsed time and Start Time < Elapsed time
        playlist = TimedAsset.objects.filter(project=self.project,
                                                           start__lte=elapsed_time,
                                                           end__gte=elapsed_time)

        # Make a list of all assets that aren't banned
        # and are in self.all, ensuring that tag filters are applied
        self.playlist_timed = [item.asset for item in playlist
                               if not self._banned(item.asset) and item.asset in self.all]

        # apply project ordering
        self.playlist_timed = self.order_assets(self.playlist_timed)

        # logger.debug("Found timed assets: %s" % self.playlist_timed)
