# Django settings for roundware project.
import os

DEBUG = True
#TEMPLATE_DEBUG = DEBUG
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('round', 'your_email@example.com'),
)

######## ROUNDWARE SPECIFIC SETTINGS ###########
# url base for media files
MEDIA_BASE_URI = "http://roundware.org/rwmedia/" 
# external url where audio files can be accessed
AUDIO_FILE_URI = MEDIA_BASE_URI # + "audio"
# external url where video files can be accessed
VIDEO_FILE_URI = AUDIO_FILE_URI #MEDIA_BASE_URI + "video"
# external url where image files can be accessed
IMAGE_FILE_URI = AUDIO_FILE_URI #MEDIA_BASE_URI + "img"

MEDIA_ROOT = ''
MEDIA_BASE_DIR = "/var/www/rwmedia/"
# internal path name to media file directories
AUDIO_FILE_DIR = MEDIA_BASE_DIR #+ "audio"
VIDEO_FILE_DIR = MEDIA_BASE_DIR #+ "video"
IMAGE_FILE_DIR = MEDIA_BASE_DIR #+ "img"

ALLOWED_AUDIO_MIME_TYPES = ['audio/x-wav', 'audio/mpeg', 'audio/mp4a-latm', 'audio/x-caf',  'audio/mp3',  ]
ALLOWED_IMAGE_MIME_TYPES = ['image/jpeg', 'image/gif', 'image/png', 'image/pjpeg', ]
ALLOWED_TEXT_MIME_TYPES = ['text/plain', 'text/html', 'application/xml', ]
ALLOWED_MIME_TYPES = ALLOWED_AUDIO_MIME_TYPES + ALLOWED_IMAGE_MIME_TYPES + ALLOWED_TEXT_MIME_TYPES

 # session_id assigned to files that are uploaded through the admin
# MUST correspond to session_id that exists in session table
DEFAULT_SESSION_ID = "-1"
API_URL = "http://roundware.com/roundware/"
MANAGERS = ADMINS
# change this to the proper id for AnonymousUser in database for Guardian
ANONYMOUS_USER_ID = 0
# settings for notifications module
# this is the email account from which notifications will be sent
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'email@gmail.com'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

LISTEN_UIMODE = "listen"
SPEAK_UIMODE = "speak"

######## END ROUNDWARE SPECIFIC SETTINGS #########

#change this to reflect your environment
#JSS: this will always set PROJECT_PATH to the directory in which settings.py is contained
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.

        'NAME': 'roundware',                      # Or path to database file if using sqlite3.
        'USER': 'round',                      # Not used with sqlite3.
        'PASSWORD': 'password',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = PROJECT_PATH + '/static'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '2am)ks1i88hss27e7uri%$#v4717ms6p869)2%cc*w7oe61q6^'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'roundware.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #os.path.join(PROJECT_PATH, 'templates')
    PROJECT_PATH + '/templates',
    PROJECT_PATH + '/rw/templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'roundware.rw',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',

    #this will allow for google maps integration in the admin
    'guardian',
    'chartit',
    'roundware.notifications',
    'south',
    'validatedfile',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
}

# don't use MemoryFileUploadHandler since we want to scan from file path
# for viruses.  Buffer scanning with pyclamav is not fully secure and is not
# included in recent versions.
FILE_UPLOAD_HANDLERS = (
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
)


# PROFILING using django-profiler
if DEBUG:
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

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
        'TIMEOUT': 60,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}


# Load the local settings file
try:
    from local_settings import *
except ImportError:
    pass
