# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from django.test import TestCase
from django.conf import settings

from model_mommy import mommy
from model_mommy.generators import gen_file_field

from roundware.settings import DEFAULT_SESSION_ID
from roundware.rw.models import (Language, LocalizedString,
                                 Tag, TagCategory, Session)


def validated_file_field_gen():
    return gen_file_field()


class FakeRequest(object):

    def __init__(self):
        self.GET = {}

    def get_host(self):
        return 'rw.com'


def mock_distance_in_meters_near(l_lat, l_long, rec_lat, rec_long):
    return 1


def mock_distance_in_meters_far(l_lat, l_long, rec_lat, rec_long):
    return 10000000000


class RoundwaredTestCase(TestCase):

    """ provide common testcase data for Roundwared test cases 
    """

    def setUp(self):
        self.maxDiff = None

        generator_dict = {
            'validatedfile.fields.ValidatedFileField':
            validated_file_field_gen
        }
        # can't set this directly in settings: db ENGINE not yet available
        setattr(settings, 'MOMMY_CUSTOM_FIELDS_GEN', generator_dict)

        self.default_session = mommy.make(Session, id=DEFAULT_SESSION_ID)
        self.english = mommy.make(Language, language_code='en')
        self.spanish = mommy.make(Language, language_code='es')
        self.english_msg = mommy.make(LocalizedString, localized_string="One",
                                      language=self.english)
        self.spanish_msg = mommy.make(LocalizedString, localized_string="Uno",
                                      language=self.spanish)
        self.tagcat1 = mommy.make(TagCategory, name='tagcatname')
        self.tag1 = mommy.make(Tag, data="{'json':'value'}",
                               loc_msg=[self.english_msg, self.spanish_msg],
                               tag_category=self.tagcat1,
                               value='tag1', id=1)
