#MODES: True Shuffle, Random cycle N times

import logging
import random
import threading
from profiling import profile
from roundwared import gpsmixer
from roundware.rw import models
from roundwared import db
from operator import itemgetter, attrgetter


class RecordingCollection:
    ######################################################################
    # Public
    ######################################################################
    def __init__(self, stream, request, radius, ordering='random'):
        self.radius = radius
        self.stream = stream
        self.request = request
        logging.debug("RecordingCollection init - request: " + str(request))
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
        logging.debug("update_request")
        self.lock.acquire()
        self.all_recordings = db.get_recordings(request)
        self.far_recordings = self.all_recordings
        self.nearby_played_recordings = []
        self.nearby_unplayed_recordings = []
        self.update_nearby_recordings(request)
        logging.debug("update_request: all_recordings count: " + str(len(self.all_recordings))
                      + ", far_recordings count: " + str(len(self.far_recordings))
                      + ", nearby_played_recordings count: " + str(len(self.nearby_played_recordings))
                      + ", nearby_unplayed_recordings count: " + str(len(self.nearby_unplayed_recordings)))
        self.lock.release()

    # Gets a new recording to play.
    # @profile(stats=True)
    def get_recording(self):
        logging.debug("Recording Collection: Getting a recording from the bucket.")
        self.lock.acquire()
        recording = None
        logging.debug("Recording Collection: we have " + str(len(self.nearby_unplayed_recordings)) + " unplayed recs.")
        if len(self.nearby_unplayed_recordings) > 0:
#           index = random.randint(0, len(self.nearby_unplayed_recordings) - 1)
            index = 0
            recording = self.nearby_unplayed_recordings.pop(index)
            logging.debug("RecordingCollection: get_recording: Got " + recording.filename)
            self.nearby_played_recordings.append(recording)
        elif len(self.nearby_played_recordings) > 0:
            logging.debug("!!!!!!!!!!!!!!!!!get_recording 1")
            logging.debug("!!!!!!!!!!!!!!!!!get_recording request:  " + str(self.request))
            p = models.Project.objects.get(id=int(self.request['project_id']))
            logging.debug("!!!!!!!!!!!!!!!!!get_recording 2 - repeatmode:" + p.repeat_mode.mode)
            #do this only if project setting calls for it
            if p.repeat_mode.id == 2:
                logging.debug("!!!!!!!!!!!!!!!!!get_recording continuous mode")
                self.all_recordings = db.get_recordings(self.request)
                self.far_recordings = self.all_recordings
                self.nearby_played_recordings = []
                self.nearby_unplayed_recordings = []
                self.update_nearby_recordings(self.request)
                logging.debug("GET_RECORDING UPDATE: all_recordings count: " + str(len(self.all_recordings))
                          + ", far_recordings count: " + str(len(self.far_recordings))
                          + ", nearby_played_recordings count: " + str(len(self.nearby_played_recordings))
                          + ", nearby_unplayed_recordings count: " + str(len(self.nearby_unplayed_recordings)))
                index = 0
                recording = self.nearby_unplayed_recordings.pop(index)
                logging.debug("POST UPDATE RecordingCollection: get_recording: Got " + recording.filename)
                self.nearby_played_recordings.append(recording)
            else:
                logging.debug("!!!!!!!!!!!!!!!!!get_recording stop mode")

        self.lock.release()
        return recording

    def add_recording(self, asset_id):
        self.lock.acquire()
        logging.debug("add_recording enter - asset id: " + str(asset_id))
        a = models.Asset.objects.get(id=str(asset_id))
        self.nearby_unplayed_recordings.insert(0, a)
        logging.debug("add_recording exit")
        self.lock.release()

    #Updates the collection of recordings according to a new listener position.
    def move_listener(self, listener):
        #logging.debug("move_listener")
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

        logging.debug('Ordering is: ' + self.ordering)
        if self.ordering == 'random':
            random.shuffle(new_nearby_unplayed_recordings)
        elif self.ordering == 'by_like':
            new_nearby_unplayed_recordings = \
                self.order_assets_by_like(new_nearby_unplayed_recordings)
        elif self.ordering == 'by_weight':
            new_nearby_unplayed_recordings = \
                self.order_assets_by_weight(new_nearby_unplayed_recordings)

        self.far_recordings = new_far_recordings
        self.nearby_unplayed_recordings = new_nearby_unplayed_recordings
        self.nearby_played_recordings = new_nearby_played_recordings

    def order_assets_by_like(self, assets):
        unplayed = []
        for asset in assets:
            count = models.Asset.get_likes(asset)
            unplayed.append((count, asset))
        logging.info('Unordered: ' +
                     str([(u[0], u[1].filename) for u in unplayed]))
        unplayed = sorted(unplayed, key=itemgetter(0), reverse=True)
        logging.info('Ordered by like: ' +
                     str([(u[0], u[1].filename) for u in unplayed]))
        return [x[1] for x in unplayed]

    def order_assets_by_weight(self, assets):
        unplayed = []
        for asset in assets:
            weight = asset.weight
            unplayed.append((weight, asset))
        logging.debug('Unordered: ' +
                      str([(u[0], u[1].filename) for u in unplayed]))
        unplayed = sorted(unplayed, key=itemgetter(0), reverse=True)
        logging.debug('Ordered by weighting: ' +
                      str([(u[0], u[1].filename) for u in unplayed]))
        return [x[1] for x in unplayed]

    #True if the listener and recording are close enough to be heard.
    def is_nearby(self, listener, recording):
        if listener.has_key('latitude') \
            and listener['latitude'] \
            and listener['longitude']:

            distance = gpsmixer.distance_in_meters(
                listener['latitude'], listener['longitude'],
                recording.latitude, recording.longitude)

            return distance <= self.radius
        else:
            return True
