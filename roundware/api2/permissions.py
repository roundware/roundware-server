# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from rest_framework.permissions import BasePermission, SAFE_METHODS


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
