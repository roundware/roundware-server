from .common import *
try:
    from .local_settings import *
except ImportError:
    pass

# Set Roundware API for internal calls to development environment
API_URL = "http://127.0.0.1:8888/roundware/"

INSTALLED_APPS = INSTALLED_APPS + (
    'discoverage',
    'debug_toolbar',
)

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR_PATCH_SETTINGS = False
CRISPY_FAIL_SILENTLY = not DEBUG

MIDDLEWARE_CLASSES = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
) + MIDDLEWARE_CLASSES

# Bypass the INTERNAL_IPS check for Debug Toolbar
class internal_list(list):
    def __contains__(self, key):
        return True
INTERNAL_IPS = internal_list()

# PROFILING using django-profiler
PROFILING_SQL_QUERIES = True
LOGGING['handlers'].update({
    'console': {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
        'formatter': 'simple'
    },
})

LOGGING['loggers'].update({
     '': {
        'level': 'DEBUG',
        'handlers': ['console'],
        'propagate': True,
     },
     'profiling': {
        'level': 'DEBUG',
        'handlers': ['console'],
        'propagate': False,
     },   
})       
