# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from django.conf.urls import url
from roundware.api2 import views

urlpatterns = [
    url(r'^$', views.APIRootView.as_view()),
    url(r'^assets/$', views.AssetList.as_view(), name='assets'),
]
