# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# Contains Roundware DRF REST API V2 signals.
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
import logging

logger = logging.getLogger(__name__)

def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Create an access Token for every new user
    """
    if created:
        Token.objects.create(user=instance)

post_save.connect(create_auth_token, get_user_model)
