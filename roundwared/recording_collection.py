# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# MODES: True Shuffle, Random cycle N times

from __future__ import unicode_literals
import logging
import threading
import os.path
from time import time
import math
try:
    from profiling import profile
except ImportError: # pragma: no cover
    pass

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point, Polygon
from geopy.distance import VincentyDistance
from roundwared import gpsmixer
from roundwared import gpsposn
from roundware.rw.models import Asset, Project, TimedAsset, Session, Vote, UserProfile
from roundwared import db
from roundwared.asset_sorters import order_assets_randomly, order_assets_by_like, order_assets_by_weight
from roundware.lib.exception import RoundException

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

        # these are lists of model.Asset objects ie [rec1,rec2,etc]
        self.all = []
        # The main list of assets to play, in reverse order because it is a stack.
        self.playlist_proximity = []
        # A list of nearby played assets. We don't want to repeat nearby assets
        # even if they are removed from the ban list(dict.)
        self.banned_proximity = []
        # A dict of temporarily banned_timeout assets, key is asset.id and value is
        # timestamp of last play time. Reset only when stream is restarted.
        self.banned_timeout = {}
        # A list of blocked assets per session's user;
        # includes assets blocked individually as well as based on their creator
        self.user_blocked_list = []
        # A stack of assets from the project's TimedAssets
        self.playlist_timed = []

        self.lock = threading.Lock()
        # initial population of list of blocked assets
        self._generate_user_blocked_list()
        self.update_request(self.request, update_proximity=False)
        # If geolisten is not enabled update the "proximity" playlist
        # @todo: Re-architect this.
        self.s = Session.objects.get(id=self.request['session_id'])
        if not self.s.geo_listen_enabled:
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
        logger.info("Asset Counts - all: %s, playlist_proximity: %s, banned_proximity: %s, banned_timeout: %s, user_blocked_list: %s." %
                     (len(self.all),
                      self.count(),
                      len(self.banned_proximity),
                      len(self.banned_timeout),
                      len(self.user_blocked_list)
                      ))
        if lock:
            self.lock.release()


    def bearing_to(self, posn_origin, posn_destination):
        lat1 = math.radians(posn_origin.coords[1])
        lat2 = math.radians(posn_destination.coords[1])
        dLon = math.radians(posn_destination.coords[0] - posn_origin.coords[0])
        y = math.sin(dLon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) \
            - math.sin(lat1) * math.cos(lat2) \
            * math.cos(dLon)
        brng = math.atan2(y, x)
        return (math.degrees(brng) + 360) % 360


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
            if self.s.geo_listen_enabled:
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
        Returns first existing item, in order, from: timed playlist if prioritized;
        proximity playlist; timed playlist if not prioritized; otherwise None
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
                # Do not clear the ban list by default so repeated playback of
                # assets still obeys BANNED_TIMEOUT_LIMIT
                # TODO: consider parameter to toggle clearing of banned_timeout
                # self.banned_timeout = {}
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

    def add_asset_to_rc(self, asset):
        self.lock.acquire()
        logger.info("adding asset id to playlist_proximity: %s " % asset.id)
        self.playlist_proximity.append(asset)
        self.lock.release()

    def remove_asset_from_rc(self, asset):
        self.lock.acquire()
        logger.debug("removing asset id from playlist_proximity: %s " % asset.id)
        if asset in self.playlist_proximity:
            self.playlist_proximity.remove(asset)
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
        return (len(self.banned_proximity) > 0 or len(self.banned_timeout) > 0)

    def order_assets(self, assets):
        """
        Order assets by ordering method set in project config
        """
        # logger.debug("Ordering assets by: %s" % self.ordering)
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
        if self.s.geo_listen_enabled:
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
            if self.s.geo_listen_enabled:
                logger.debug("Proximity banned assets: %s" %
                             self.banned_proximity)

        self.playlist_proximity = []
        for r in self.all:
            # If the asset is nearby, not nearby banned_timeout,
            # not timeout banned_timeout, and not blocked by user,
            # then add it to the list of playlist_proximity items.
            if not self._banned(r) and self._is_nearby(request, r) and not self._blocked(r):
                self.playlist_proximity.append(r)

        # apply project ordering
        self.playlist_proximity = self.order_assets(self.playlist_proximity)


    def _is_nearby(self, request, recording):
        """
        True if the request and recording are close enough to be heard
        per the active listening mode
        """
        if not self.s.geo_listen_enabled:
            return True

        # lat/lon of listener must be passed in order to check distance
        if 'latitude' in request and 'longitude' in request:
            # first, if heading param is present, use directional listening mode
            if 'listener_heading' in request and request['listener_heading'] is not None:
                R = 6371000.0  # The radius of the Earth (m)
                lh = request['listener_heading']
                # assume listener_width is 30 degrees unless passed in request
                if 'listener_width' in request and request['listener_width'] is not None:
                    lw = request['listener_width']
                else:
                    lw = 30
                # assume listener_range_min is 0 unless passed in request
                if 'listener_range_min' in request and request['listener_range_min'] is not None:
                    lr_min = request['listener_range_min']
                else:
                    lr_min = 0
                # assume listener_range_max is half the circumference of the earth unless passed in request
                if 'listener_range_max' in request and request['listener_range_max'] is not None:
                    lr_max = request['listener_range_max']
                else:
                    lr_max = math.pi * R
                center = Point(float(request['longitude']), float(request['latitude']))
                asset_location = Point(recording.longitude, recording.latitude)
                # check if asset is within distance range and heading angle range
                # first, calculate heading from listener to asset
                asset_heading = self.bearing_to(center, asset_location)
                logger.info('heading to asset %s = %s', recording.id, asset_heading)
                # calculate distance between listener and asset
                asset_distance = gpsmixer.distance_in_meters(
                    request['latitude'], request['longitude'],
                    recording.latitude, recording.longitude)
                logger.info('distance to asset %s = %s', recording.id, asset_distance)
                logger.info('lr_min / lr_max -  %s / %s', lr_min, lr_max)
                # check if asset is within distance
                if lr_min <= asset_distance <= lr_max:
                    # if so, see if within heading range
                    heading_min = lh - (lw/2)
                    heading_max = lh + (lw/2)
                    logger.info('heading_min / heading_max -  %s / %s', heading_min, heading_max)
                    if heading_min <= asset_heading <= heading_max:
                        logger.info("asset_id=%s within listener's directional ranges: true", recording.id)
                        return True
                    else:
                        logger.info("asset_id=%s within listener's directional ranges: false", recording.id)
                        return False
                else:
                    logger.info("asset_id=%s within listener's distance ranges: false", recording.id)
                    return False

            # then, if listener_range_max parameter has been passed by user with value
            elif 'listener_range_max' in request and request['listener_range_max'] is not None:
                # assume listener_range_min is 0 unless passed in request
                if 'listener_range_min' in request and request['listener_range_min'] is not None:
                    lr_min = request['listener_range_min']
                else:
                    lr_min = 0
                distance = gpsmixer.distance_in_meters(
                    request['latitude'], request['longitude'],
                    recording.latitude, recording.longitude)
                # if (distance <= request['listener_range_max'] and distance >= lr_min):
                    # logger.info("asset %s within listener_range" % recording.id)
                return (distance <= request['listener_range_max'] and distance >= lr_min)
            # then, if asset.shape exists see if listener is within shape
            elif recording.shape:
                listener_location = Point(request['longitude'], request['latitude'], srid=recording.shape.srid)
                inside = listener_location.intersects(recording.shape)
                logger.info("listener within asset_id=%s geometry: %s", recording.id, inside)
                return inside
            # finally, if no listener_heading, listener_range_max or asset.shape, use default project radius
            else:
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


    def _blocked(self, recording):
        """
        Returns whether an asset is blocked by session user.
        """
        return (recording.id in self.user_blocked_list)


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


    def _assets_by_user(self, user_id):
        """
        returns a list of asset_ids created by specified user_id
        """
        # get user's device_id
        device_id = UserProfile.objects.filter(user__id=user_id).values('device_id')
        # get sessions with that device_id
        device_sessions = Session.objects.filter(device_id=device_id).values_list('id', flat=True)
        # get asset_ids with that session_id
        user_asset_ids = Asset.objects.filter(session_id__in=device_sessions).values_list('id', flat=True)

        return user_asset_ids


    def _generate_user_blocked_list(self):
        """
        generate list of blocked assets for user based on session_id
        """
        # reset user_blocked_list as this function recalculates from scratch
        self.user_blocked_list = []
        session_id = self.request["session_id"]
        # identify user via session_id
        try:
            s = Session.objects.get(id=session_id)
        except:
            raise RoundException("session_id does not exist")

        device_id = s.device_id
        User = get_user_model()
        try:
            user = User.objects.get(userprofile__device_id=device_id)
        except:
            user = False
            logger.info("no user associated with session_id")
        if not user:
            return
        # generate list of blocked assets from vote if user exists
        asset_votes = Vote.objects.filter(voter_id=user, type='block_asset')
        for asset_vote in asset_votes:
            self.user_blocked_list.append(asset_vote.asset_id)

        # generate list of assets associated with users that are blocked
        assets_of_blocked_user = Vote.objects.filter(voter_id=user, type='block_user') \
                                             .values_list('asset_id', flat=True)
        logger.info("assets_of_blocked_user = %s", assets_of_blocked_user)
        # generate list of sessions in which blocked assets were created
        sessions_of_blocked_assets = Asset.objects.filter(id__in=assets_of_blocked_user) \
                                                  .values_list('session_id', flat=True)
        # get device_ids associated with list of sessions
        devices_of_blocked_sessions = Session.objects.filter(id__in=sessions_of_blocked_assets) \
                                                     .values_list('device_id', flat=True)
        # get the users associated with device_ids
        blocked_user_ids = User.objects.filter(userprofile__device_id__in=devices_of_blocked_sessions) \
                                       .values_list('id', flat=True)
        logger.info("blocked_user_ids = %s", blocked_user_ids)
        # generate list of asset_ids made by same user as submitted asset_id
        # and add to user_blocked_list
        for blocked_user_id in blocked_user_ids:
            blocked_user_assets = self._assets_by_user(blocked_user_id)
            # extend user_blocked_list without duplicates
            self.user_blocked_list.extend(x for x in blocked_user_assets if x not in self.user_blocked_list)
        logger.info("user_blocked_list = %s", self.user_blocked_list)
