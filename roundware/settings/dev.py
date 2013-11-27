from .common import *
try:
    from .local_settings import *
except ImportError:
    pass


INSTALLED_APPS = INSTALLED_APPS + (
    'discoverage',
)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# PROFILING using django-profiler
PROFILING_SQL_QUERIES = True
LOGGING['handlers'].update({
    'console': {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
        'formatter': 'verbose'
    },
    'profile_logfile': {
        'filename': '/var/log/rwprofiling',
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
