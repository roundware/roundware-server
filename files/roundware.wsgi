import os
import sys
import site

CODE_ROOT = '/media/sf_roundware-server'
PROJECT_ROOT = os.path.join(CODE_ROOT, 'roundware')
SITE_PACKAGES = '/home/jule/.virtualenvs/againfaster/lib/python2.6/site-packages'

sys.stdout = sys.stderr

site.addsitedir(os.path.abspath(site_packages))
sys.path.insert(0, CODE_ROOT)
sys.path.insert(1, PROJECT_ROOT)
sys.path.insert(2, os.path.join(PROJECT_ROOT))
sys.path.insert(3, SITE_PACKAGES)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
