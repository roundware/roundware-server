# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
import logging
from operator import itemgetter
import random
from roundware.rw import models
from datetime import date, timedelta
logger = logging.getLogger(__name__)


def order_assets_by_like(assets):
    """
    List is reverse order because assets are popped off the stack.
    """
    unplayed = []
    for asset in assets:
        count = models.Asset.get_likes(asset)
        unplayed.append((count, asset))
    # logger.debug('Ordering Assets by Like. Input: ' +
    #            str([(u[0], u[1].filename) for u in unplayed]))
    unplayed = sorted(unplayed, key=itemgetter(0))
    logger.debug('Ordering Assets by Like. Output: ' +
                str([(u[0], u[1].filename) for u in unplayed]))
    return [x[1] for x in unplayed]


def order_assets_by_weight(assets):
    """
    List is reverse order because assets are popped off the stack.
    """
    unplayed = []
    for asset in assets:
        weight = asset.weight
        unplayed.append((weight, asset))
    # logger.debug('Ordering Assets by Weight. Input: ' +
    #             str([(u[0], u[1].filename) for u in unplayed]))
    unplayed = sorted(unplayed, key=itemgetter(0))
    logger.debug('Ordering Assets by Weight. Output: ' +
                 str([(u[0], u[1].filename) for u in unplayed]))
    return [x[1] for x in unplayed]


def order_assets_randomly(assets):
    # logger.debug("Ordering Assets Randomly. Input: %s" % (assets,))
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
