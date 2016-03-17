"""
Roundware Server Production Settings

This file will be copied to /var/www/roundware/settings/roundware-production.py during
the Roundware Server installation.

It is used as the Django DJANGO_SETTINGS_MODULE in the WSGI file for Apache to
allow server customization of the stock settings.
"""
from roundware.settings import *

# Admin account(s) to receive error log messages.
ADMINS = (
    ('round', 'username@example.com'),
)

# The SMTP email account used for outgoing mail.
EMAIL_HOST = 'smtp.example.com'
EMAIL_HOST_USER = 'username@example.com'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Standard Django DEBUG setting
DEBUG = False
# The roundware log file /var/log/roundware detail level.
# INFO is default. Set to DEBUG for detailed information.
LOGGING['handlers']['file']['level'] = 'INFO'
