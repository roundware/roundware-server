import os
import sys
import site

SITE_PACKAGES = '/var/www/roundware/lib/python2.7/site-packages/'
PROJECT_ROOT = '/var/www/roundware/source/'
CODE_ROOT = '/var/www/roundware/source/roundware/'
ACTIVATE_VENV = '/var/www/roundware/bin/activate_this.py'

sys.stdout = sys.stderr

site.addsitedir(SITE_PACKAGES)
sys.path.append(PROJECT_ROOT)
sys.path.append(CODE_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'roundware.settings'

# Enable Virtual Environment
execfile(ACTIVATE_VENV, dict(__file__=ACTIVATE_VENV))

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

