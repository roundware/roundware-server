import os
import sys

PROJECT_ROOT = '/var/www/roundware/source/'
CODE_ROOT = '/var/www/roundware/source/roundware/'
SETTINGS_ROOT = '/var/www/roundware/settings/'

sys.stdout = sys.stderr

sys.path.append(PROJECT_ROOT)
sys.path.append(CODE_ROOT)
sys.path.append(SETTINGS_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'roundware_production'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

