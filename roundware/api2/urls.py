# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'assets', views.AssetViewSet)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^obtain_token/', 'rest_framework.authtoken.views.obtain_auth_token'),
)
