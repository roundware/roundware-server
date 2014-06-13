from .common import *
try:
    from .local_settings import *
except ImportError:
    pass


INSTALLED_APPS = INSTALLED_APPS + (
    'discoverage',
    'debug_toolbar',
)

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR_PATCH_SETTINGS = False  # setup debug toolbar explicitly
CRISPY_FAIL_SILENTLY = not DEBUG

MIDDLEWARE_CLASSES = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
) + MIDDLEWARE_CLASSES


# PROFILING using django-profiler
PROFILING_SQL_QUERIES = True
LOGGING['handlers'].update({
    'console': {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
        'formatter': 'verbose'
    },
    'profile_logfile': {
        'filename': 'rwprofiling',
        'level': 'DEBUG',
        'class': 'logging.FileHandler',
        'formatter': 'verbose'
    },        
})

LOGGING['loggers'].update({
     'profiling': {
        'level': 'DEBUG',
        'handlers': ['console','profile_logfile'],
        'propagate': False,
     },   
})       
