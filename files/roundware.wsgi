import os
import sys
import site

CODE_ROOT = '/home/ubuntu/roundware-server/roundware/'
PROJECT_ROOT = os.path.join(CODE_ROOT, 'roundware')
SITE_PACKAGES = '/usr/pythonenv/roundware-server/lib/python2.7/site-packages/'

sys.stdout = sys.stderr

site.addsitedir(os.path.abspath(SITE_PACKAGES))
sys.path.insert(0, CODE_ROOT)
sys.path.insert(1, PROJECT_ROOT)
sys.path.insert(2, os.path.join(PROJECT_ROOT))
sys.path.insert(3, SITE_PACKAGES)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
