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


# MODES: True Shuffle, Random cycle N times

from __future__ import unicode_literals
import logging
import threading
import asset_sorters
try:
    from profiling import profile
except ImportError:
    pass
from roundware.rw.models import Tag
from roundwared import gpsmixer
from roundware.rw import models
from roundwared import db
from operator import itemgetter
from roundwared.asset_sorters import order_assets_randomly, order_assets_by_like, order_assets_by_weight

logger = logging.getLogger(__name__)


class RecordingCollection:
    ######################################################################
    # Public
    ######################################################################

    def __init__(self, stream, request, radius, ordering='random'):
        self.radius = radius
        self.stream = stream
        self.request = request
        logger.debug("RecordingCollection init - request: " + str(request))
        # these are lists of model.Recording objects ie [rec1,rec2,etc]
        self.all_recordings = []
        self.far_recordings = []
        self.nearby_played_recordings = []
        self.nearby_unplayed_recordings = []
        self.ordering = ordering
        self.lock = threading.Lock()
        self.update_request(self.request)

    # Updates the request stored in the collection.
    # @profile(stats=True)
    def update_request(self, request):
        logger.debug("update_request")
        self.lock.acquire()
        self.all_recordings = db.get_recordings(request)
        self.far_recordings = self.all_recordings
        self.nearby_played_recordings = []
        self.nearby_unplayed_recordings = []
        self.update_nearby_recordings(request)
        logger.debug("update_request: all_recordings count: " + str(len(self.all_recordings))
                     + ", far_recordings count: " +
                     str(len(self.far_recordings))
                     + ", nearby_played_recordings count: " +
                     str(len(self.nearby_played_recordings))
                     + ", nearby_unplayed_recordings count: " + str(len(self.nearby_unplayed_recordings)))
        self.lock.release()

    # Gets a new recording to play.
    # @profile(stats=True)
    def get_recording(self):
        logger.debug(
            "Recording Collection: Getting a recording from the bucket.")
        self.lock.acquire()
        recording = None
        logger.debug("Recording Collection: we have " +
                     str(len(self.nearby_unplayed_recordings)) + " unplayed recs.")
        if len(self.nearby_unplayed_recordings) > 0:
            #           index = random.randint(0, len(self.nearby_unplayed_recordings) - 1)
            index = 0
            recording = self.nearby_unplayed_recordings.pop(index)
            logger.debug(
                "RecordingCollection: get_recording: Got " + str(recording.filename))
            self.nearby_played_recordings.append(recording)
        elif len(self.nearby_played_recordings) > 0:
            logger.debug("get_recording 1")
            logger.debug("get_recording request:  " + str(self.request))
            p = models.Project.objects.get(id=int(self.request['project_id']))
            logger.debug("get_recording 2 - repeatmode:" + p.repeat_mode.mode)
            # do this only if project setting calls for it
            if p.is_continuous():
                logger.debug("get_recording continuous mode")
                self.all_recordings = db.get_recordings(self.request)
                self.far_recordings = self.all_recordings
                self.nearby_played_recordings = []
                self.nearby_unplayed_recordings = []
                self.update_nearby_recordings(self.request)
                logger.debug("GET_RECORDING UPDATE: all_recordings count: " + str(len(self.all_recordings))
                             + ", far_recordings count: " +
                             str(len(self.far_recordings))
                             + ", nearby_played_recordings count: " +
                             str(len(self.nearby_played_recordings))
                             + ", nearby_unplayed_recordings count: " + str(len(self.nearby_unplayed_recordings)))
                index = 0
                recording = self.nearby_unplayed_recordings.pop(index)
                logger.debug(
                    "POST UPDATE RecordingCollection: get_recording: Got " + str(recording.filename))
                self.nearby_played_recordings.append(recording)
            else:
                logger.debug("get_recording stop mode")

        self.lock.release()
        return recording

    def add_recording(self, asset_id):
        self.lock.acquire()
        logger.debug("add_recording enter - asset id: " + str(asset_id))
        a = models.Asset.objects.get(id=str(asset_id))
        self.nearby_unplayed_recordings.insert(0, a)
        logger.debug("add_recording exit")
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
            self.nearby_unplayed_recordings)

    # True if the collection has any recordings left to play.
    def has_recording(self):
        return len(self.nearby_unplayed_recordings) > 0

    ######################################################################
    # Private
    ######################################################################

    def update_nearby_recordings(self, listener):
        new_far_recordings = []
        new_nearby_unplayed_recordings = []
        new_nearby_played_recordings = []

        for r in self.far_recordings:
            if self.is_nearby(listener, r):
                new_nearby_unplayed_recordings.append(r)
            else:
                new_far_recordings.append(r)

        for r in self.nearby_unplayed_recordings:
            if self.is_nearby(listener, r):
                new_nearby_unplayed_recordings.append(r)
            else:
                new_far_recordings.append(r)

        for r in self.nearby_played_recordings:
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

        self.far_recordings = new_far_recordings
        self.nearby_unplayed_recordings = new_nearby_unplayed_recordings
        self.nearby_played_recordings = new_nearby_played_recordings

    # Moved to roundwared/asset_sorters
    # def order_assets_by_like(self, assets):
    #     unplayed = []
    #     for asset in assets:
    #         count = models.Asset.get_likes(asset)
    #         unplayed.append((count, asset))
    #     logger.info('Unordered: ' +
    #                  str([(u[0], u[1].filename) for u in unplayed]))
    #     unplayed = sorted(unplayed, key=itemgetter(0), reverse=True)
    #     logger.info('Ordered by like: ' +
    #                  str([(u[0], u[1].filename) for u in unplayed]))
    #     return [x[1] for x in unplayed]

    # def order_assets_by_weight(self, assets):
    #     unplayed = []
    #     for asset in assets:
    #         weight = asset.weight
    #         unplayed.append((weight, asset))
    #     logger.debug('Unordered: ' +
    #                   str([(u[0], u[1].filename) for u in unplayed]))
    #     unplayed = sorted(unplayed, key=itemgetter(0), reverse=True)
    #     logger.debug('Ordered by weighting: ' +
    #                   str([(u[0], u[1].filename) for u in unplayed]))
    #     return [x[1] for x in unplayed]

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
