# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from rest_framework.permissions import BasePermission, SAFE_METHODS
import logging

logger = logging.getLogger(__name__)


class AuthenticatedReadAdminWrite(BasePermission):
    """
    User can read the data if authenticated and write if admin.
    """

    def has_permission(self, request, view):
        if (request.user and request.user.is_authenticated()):
            # Return true for GET, OPTIONS, HEAD.
            if request.method in SAFE_METHODS:
                return True
            # Return true for other methods if admin
            if request.user.is_staff:
                return True
        return False
