from tastypie.resources import ModelResource
from roundware.rw.models import Asset, Project, Event, Session


class AssetResource(ModelResource):
    class Meta:
        queryset = Asset.objects.all()
        resource_name = "asset"
        allowed_methods = ['get']


class ProjectResource(ModelResource):
    class Meta:
        queryset = Project.objects.all()
        resource_name = "project"
        allowed_methods = ['get']


class EventResource(ModelResource):
    class Meta:
        queryset = Event.objects.all()
        resource_name = "event"
        allowed_methods = ['get']


class SessionResource(ModelResource):
    class Meta:
        queryset = Session.objects.all()
        resource_name = "session"
        allowed_methods = ['get']
