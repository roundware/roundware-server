from django.core import cache
from django.test import TestCase
from django.conf import settings

from mock import patch
from model_mommy.generators import gen_file_field


TESTS_APPS = ('rw',)  # django-discoverage


def use_locmemcache(module, varname):
    locmem_cache = cache.get_cache(
        'django.core.cache.backends.locmem.LocMemCache')
    locmem_cache.clear()
    return patch.object(module, varname, locmem_cache)


class FakeRequest():
    pass


def rw_validated_file_field_gen():
    return gen_file_field()


class RWTestCase(TestCase):

    """ provide common testcase data for roundware.rw test cases 
    """

    def setUp(self):
        self.maxDiff = None

        generator_dict = {
            'roundware.rw.fields.RWValidatedFileField':
            rw_validated_file_field_gen
        }
        # can't set this directly in settings: db ENGINE not yet available
        setattr(settings, 'MOMMY_CUSTOM_FIELDS_GEN', generator_dict)
