from __future__ import unicode_literals
import os
# Patch datetime field parser to support ISO 8601 Date/Time strings.
# More details here: https://github.com/tomchristie/django-rest-framework/issues/1338
from dateutil import parser
from django.forms import fields
fields.DateTimeField.strptime = lambda o, v, f: parser.parse(v)


DEBUG = False
TEMPLATE_DEBUG = False
# True when unit tests are running. Used by roundwared.recording_collection
TESTING = False
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

ADMINS = (
    ('round', 'your_email@example.com'),
)

# here() gives us file paths from the root of the system to the directory
# holding the current file.
here = lambda * x: os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

# Root of roundware Django project
PROJECT_ROOT = here("../..")

# Root of roundware-server
ROUNDWARE_SERVER_ROOT = here("../..")

# root() gives us file paths from the root of the system to whatever
# folder(s) we pass it starting at the roundware-server root
root = lambda * x: os.path.join(os.path.abspath(PROJECT_ROOT), *x)

# Roundwared & rwstreamd.py settings
ICECAST_PORT = "8000"
ICECAST_HOST = "localhost"
ICECAST_USERNAME = "admin"
ICECAST_PASSWORD = "roundice"
ICECAST_SOURCE_USERNAME = "source"
ICECAST_SOURCE_PASSWORD = "roundice"
# Discrete steps
NUM_PAN_STEPS = 200
# In milliseconds
STEREO_PAN_INTERVAL = 10
# In milliseconds
PING_INTERVAL = 10000
MASTER_VOLUME = 3.0
HEARTBEAT_TIMEOUT = 200
# Radius in meters - default system wide setting
RECORDING_RADIUS = 1
DEMO_STREAM_CPU_LIMIT = 50.0

ALLOWED_AUDIO_MIME_TYPES = ['audio/x-wav', 'audio/wav',
                            'audio/mpeg', 'audio/mp4a-latm', 'audio/x-caf',
                            'audio/mp3', 'video/quicktime']
ALLOWED_IMAGE_MIME_TYPES = ['image/jpeg', 'image/gif', 'image/png', 'image/pjpeg']
ALLOWED_TEXT_MIME_TYPES = ['text/plain', 'text/html', 'application/xml']
ALLOWED_VIDEO_MIME_TYPES = ['video/quicktime']
ALLOWED_MIME_TYPES = ALLOWED_AUDIO_MIME_TYPES + ALLOWED_IMAGE_MIME_TYPES \
    + ALLOWED_TEXT_MIME_TYPES + ALLOWED_VIDEO_MIME_TYPES

# session_id assigned to files that are uploaded through the admin
# MUST correspond to session_id that exists in session table
DEFAULT_SESSION_ID = "-10"
MANAGERS = ADMINS
# change this to the proper id for AnonymousUser in database for Guardian
ANONYMOUS_USER_ID = -1

# The email account from which notifications will be sent
EMAIL_HOST = 'smtp.example.com'
EMAIL_HOST_USER = 'email@example.com'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

STARTUP_NOTIFICATION_MESSAGE = ""
# Number of seconds to ban an asset/recording from playing again
BANNED_TIMEOUT_LIMIT = 1800
######## END ROUNDWARE SPECIFIC SETTINGS #########

# change this to reflect your environment
# JSS: this will always set PROJECT_PATH to the directory in which
# settings.py is contained
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or
        # 'oracle'.
        'ENGINE': 'django.db.backends.mysql',

        # Or path to database file if using sqlite3.
        'NAME': 'roundware',
        'USER': 'round',
        'PASSWORD': 'round',
        'HOST': '',
        'PORT': '',
    }
}

# copy this to local_settings.py and uncomment.
# only requests to this domain will be allowed
ALLOWED_HOSTS = ['*', ]

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
MEDIA_ROOT = '/var/www/roundware/rwmedia/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/rwmedia/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# This should be the path to the 'static' directory at the root of the
# roundware-server installation.
# Example: "/home/ubuntu/roundware-server/static/"
STATIC_ROOT = "/var/www/roundware/static/"

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
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'roundware.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # os.path.join(PROJECT_PATH, 'templates')
    PROJECT_PATH + '/../templates',
    PROJECT_PATH + '/../rw/templates/rw',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_admin_bootstrapped.bootstrap3',
    'django_admin_bootstrapped',
    'django.contrib.admin.apps.SimpleAdminConfig',
    'guardian',
    'chartit',
    'validatedfile',
    'adminplus',
    'crispy_forms',
    'floppyforms',
    'djangoformsetjs',
    'sortedm2m',
    'rest_framework',
    'rest_framework.authtoken',
    'roundware.lib',
    'roundware.rw',
    'roundware.notifications',
    'roundware.api1',
    'roundware.api2',
)

REST_FRAMEWORK = {
    'PAGINATE_BY': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}

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
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/roundware',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        # The roundware system logger.
        'roundware': {
            'level': 'DEBUG',
            'handlers': ['file', 'mail_admins'],
        },
        # The roundwared stream manager logger.
        'roundwared': {
            'level': 'DEBUG',
            'handlers': ['file', 'mail_admins'],
        },
    },
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s <%(name)s.%(funcName)s:%(lineno)s> %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': "%(asctime)s %(levelname)s <%(name)s.%(funcName)s:%(lineno)s> %(message)s",
            'datefmt': "%H:%M:%S"
        },
    },
}

# don't use MemoryFileUploadHandler since we want to scan from file path
# for viruses.  Buffer scanning with pyclamav is not fully secure and is not
# included in recent versions.
FILE_UPLOAD_HANDLERS = (
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
)

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

# use Twitter Bootstrap template pack for django-crispy-forms
CRISPY_TEMPLATE_PACK = 'bootstrap'
