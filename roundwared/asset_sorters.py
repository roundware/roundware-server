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
from operator import itemgetter
import random
from roundware.rw import models
from datetime import date, timedelta
logger = logging.getLogger(__name__)


def order_assets_by_like(assets):
    unplayed = []
    for asset in assets:
        count = models.Asset.get_likes(asset)
        unplayed.append((count, asset))
    logger.info('Ordering Assets by Like. Input: ' +
                str([(u[0], u[1].filename) for u in unplayed]))
    unplayed = sorted(unplayed, key=itemgetter(0), reverse=True)
    logger.info('Ordering Assets by Like. Output: ' +
                str([(u[0], u[1].filename) for u in unplayed]))
    return [x[1] for x in unplayed]


def order_assets_by_weight(assets):
    unplayed = []
    for asset in assets:
        weight = asset.weight
        unplayed.append((weight, asset))
    logger.debug('Ordering Assets by Weight. Input: ' +
                 str([(u[0], u[1].filename) for u in unplayed]))
    unplayed = sorted(unplayed, key=itemgetter(0), reverse=True)
    logger.debug('Ordering Assets by Weight. Output: ' +
                 str([(u[0], u[1].filename) for u in unplayed]))
    return [x[1] for x in unplayed]


def order_assets_randomly(assets):
    logger.debug("Ordering Assets Randomly. Input: %s" % (assets,))
    random.shuffle(assets)
    logger.debug("Ordering Assets Randomly. Output: %s" % (assets,))
    return assets


def _within_10km(*args, **kwargs):
    if "assets" in kwargs and "request" in kwargs:
        assets = kwargs["assets"]
        listener = kwargs["request"]
    else:
        raise TypeError("Function requires assets=[] and request=")

    returning_assets = (
        [asset for asset in assets if asset.distance(listener) <= 10000])
    return returning_assets


def _ten_most_recent_days(*args, **kwargs):
    if "assets" in kwargs:
        assets = kwargs["assets"]
    else:
        raise TypeError("Function requires assets=[]")

    returning_assets = ([asset for asset in assets if date(
        asset.created.year, asset.created.month, asset.created.day) >= (date.today() - timedelta(10))])
    logger.debug("returning filtered assets: %s" % (returning_assets,))
    return returning_assets
