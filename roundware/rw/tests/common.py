# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from django.test import TestCase
from django.utils import cache
from model_bakery import baker

from roundware.rw.models import (Language, LocalizedString,
                                 Tag, TagCategory, Session)

from mock import patch


def use_locmemcache(module, varname):
    locmem_cache = cache.caches['locmemcache']
    locmem_cache.clear()
    return patch.object(module, varname, locmem_cache)


TEST_LOCATIONS = {
    "point_far_away_from_speaker": dict(latitude='-0.1', longitude='0.1'),
    # this is about 960m from the edge of the test polygon "crazy_shape"
    "point_less_than_1km_from_speaker": dict(latitude='-0.3703', longitude='-1.0441'),
    "point_in_speaker": dict(latitude='0.1', longitude='-0.1')
}

TEST_POLYGONS = {
    "crazy_shape": "MULTIPOLYGON(((-0.774183051414968 -0.120296667618684,-0.697181433024807 0.197879831012361,-0.52645517133469 0.200040922932489,-0.444333678369823 -0.0571290155627506,-0.468105689491232 -0.245144012613892,-0.774183051414968 -0.120296667618684)),((-1.25042096457759 0.204363106772745,-1.01702303720376 0.504754883670546,-0.599932296619044 0.625776031197718,-0.152586269152534 0.448566493747217,0.0354287278986072 0.00122046628070716,-0.109364430749973 -0.30349349445735,-0.340601266203676 -0.487186307668236,-0.811719304791594 -0.487186307668236,-1.0969834382485 -0.331587689419015,-1.25042096457759 0.204363106772745),(-0.774183051414968 -0.120296667618684,-0.811719304791594 -0.275399299495685,-0.504844252133409 -0.374809527821576,-0.314668163162139 -0.327265505578759,-0.239029945957657 -0.0506457398023664,-0.362212185404957 0.325384254299917,-0.796591661350698 0.35563954118171,-0.880874246235692 0.122241613807879,-0.958673555360303 -0.0917064862847996,-0.889518613916205 -0.0247126367608296,-0.796591661350698 -0.111156313565952,-0.774183051414968 -0.120296667618684)))",
    "square": "MULTIPOLYGON(((10 10, 10 20, 20 20, 20 10, 10 10)))"
}


class RWTestCase(TestCase):

    """ provide common testcase data for roundware.rw test cases
    """

    def setUp(self):
        self.maxDiff = None
        self.default_session = baker.make(Session)
        self.english = baker.make(Language, language_code='en', id=1)
        self.spanish = baker.make(Language, language_code='es', id=2)
        self.english_msg = baker.make(LocalizedString, localized_string="One",
                                      language=self.english)
        self.spanish_msg = baker.make(LocalizedString, localized_string="Uno",
                                      language=self.spanish)
        self.tagcat1 = baker.make(TagCategory, name='tagcatname')
        self.tag1 = baker.make(Tag, data="{'json':'value'}",
                               loc_msg=[self.english_msg, self.spanish_msg],
                               tag_category=self.tagcat1,
                               value='tag1', id=1)


class FakeRequest(object):

    def __init__(self):
        self.GET = {}

    def get_host(self):
        return 'rw.com'


def mock_distance_in_meters_near(l_lat, l_long, rec_lat, rec_long):
    return 1


def mock_distance_in_meters_far(l_lat, l_long, rec_lat, rec_long):
    return 10000000000
