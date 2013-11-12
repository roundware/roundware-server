from .common import *
try:
    from .local_settings import *
except ImportError:
    pass


INSTALLED_APPS = INSTALLED_APPS + (
    'django_coverage',
)

DEBUG = True
TEMPLATE_DEBUG = DEBUG