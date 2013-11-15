from django.core import cache

from mock import patch


def use_locmemcache(module, varname):
    locmem_cache = cache.get_cache(
        'django.core.cache.backends.locmem.LocMemCache')
    locmem_cache.clear()
    return patch.object(module, varname, locmem_cache)


class FakeRequest():
    pass
