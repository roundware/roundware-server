from django.conf.urls import patterns, url

from roundware.rw import forms, views

urlpatterns = patterns('',
     url(r'^tags/batch_add$', views.MultiCreateTagsView.as_view(), ),
)