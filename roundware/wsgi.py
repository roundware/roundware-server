import os
import sys
import site

SITE_PACKAGES = '/var/www/roundware/lib/python2.7/site-packages/'
PROJECT_ROOT = '/var/www/roundware/source/'
CODE_ROOT = '/var/www/roundware/source/roundware/'
SETTINGS_ROOT = '/var/www/roundware/settings/'
ACTIVATE_VENV = '/var/www/roundware/bin/activate_this.py'

sys.stdout = sys.stderr

site.addsitedir(SITE_PACKAGES)
sys.path.append(PROJECT_ROOT)
sys.path.append(CODE_ROOT)
sys.path.append(SETTINGS_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'roundware_production'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

