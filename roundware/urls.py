from django.conf import settings
from django.conf.urls import patterns, url, include

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from adminplus.sites import AdminSitePlus

from roundware.rw import urls as rw_urls

# from roundware.rw import forms

admin.site = AdminSitePlus()
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'roundware.views.home', name='home'),
    # url(r'^charts/asset/$', 'rw.views.chart_views'),
    url(r'^dashboard/$', 'rw.views.chart_views'),

    url(r'^roundware/$', 'rw.views.main'),
    url(r'^roundware$', 'rw.views.main'),

    # use admin login as overall login
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'template_name': 'admin/login.html'}),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),

     url(r'^rw/', include(rw_urls)),
)


if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += patterns('',
            url(r'^__debug__/', include(debug_toolbar.urls)),
        )
    except:
        pass


