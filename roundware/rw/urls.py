from django.conf.urls import patterns, url

from roundware.rw import views

urlpatterns = patterns('',
     url(r'^tags/batch_add$', views.MultiCreateTagsView.as_view()),
     # url(r'^masteruis/(?P<pk>\d+)/setup_tag_ui/$', 
     #    views.SetupTagUIView.as_view()),   
     url(r'^masteruis/(?P<pk>\d+)/setup_tag_ui/$', 
        views.MasterUIMappingsOrganizationView.as_view()),   
     url(r'^masteruis/setup_tag_ui/$', 
        views.MasterUIMappingsOrganizationView.as_view()),   

)