from django.conf.urls import patterns, url, include

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from tastypie.api import Api
from roundware.rw.api import AssetResource, SessionResource, EventResource, ProjectResource

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(AssetResource())
v1_api.register(ProjectResource())
v1_api.register(EventResource())
v1_api.register(SessionResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'roundware.views.home', name='home'),
#    url(r'^charts/asset/$', 'rw.views.chart_views'),
    url(r'^dashboard/$', 'rw.views.chart_views'),

    #TastyPie API URLS
    url(r'^roundware/api/', include(v1_api.urls)),

    url(r'^roundware/$', 'rw.views.main'),
    url(r'^roundware$', 'rw.views.main'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
