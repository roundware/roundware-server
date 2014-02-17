from tastypie.resources import ModelResource
from tastypie import fields
from roundware.rw.models import Asset, Project, Event, Session, ListeningHistoryItem
from roundware.rw.serializers import PrettyJSONSerializer


class AssetResource(ModelResource):
    project = fields.IntegerField(attribute="project_id")
    language = fields.IntegerField(attribute="language_id")
    session = fields.IntegerField(attribute="session_id")
    audiolength_in_seconds = fields.FloatField(attribute="audiolength_in_seconds")

    class Meta:
        queryset = Asset.objects.all()
        resource_name = "asset"
        allowed_methods = ['get']
        serializer = PrettyJSONSerializer()
        filtering = {
            "mediatype": ('exact', 'startswith',),
            "submitted": ('exact'),
            "created"  : ('exact', 'gte', 'lte', 'range'),
            "project"  : ('exact'),
            "audiolength"  : ('gte', 'lte'),
            "language"  : ('exact'),
            "session"  : ('exact'),
        }


class ProjectResource(ModelResource):
    class Meta:
        queryset = Project.objects.all()
        resource_name = "project"
        allowed_methods = ['get']
        serializer = PrettyJSONSerializer()


class EventResource(ModelResource):
    session = fields.IntegerField(attribute="session_id")

    class Meta:
        queryset = Event.objects.all()
        resource_name = "event"
        allowed_methods = ['get']
        serializer = PrettyJSONSerializer()
        filtering = {
            "event_type": ('exact', 'startswith',),
            "server_time"  : ('exact', 'gte', 'lte', 'range'),
            "session"  : ('exact'),
        }


class SessionResource(ModelResource):
    project = fields.IntegerField(attribute="project_id")
    language = fields.IntegerField(attribute="language_id")

    class Meta:
        queryset = Session.objects.all()
        resource_name = "session"
        allowed_methods = ['get']
        serializer = PrettyJSONSerializer()
        filtering = {
            "client_type": ('exact', 'contains',),
            "client_system"  : ('exact', 'contains'),
            "starttime"  : ('exact', 'gte', 'lte', 'range'),
            "demo_stream_enabled"  : ('exact'),
            "project"  : ('exact'),
            "language"  : ('exact'),
        }


class ListeningHistoryItemResource(ModelResource):
    session = fields.IntegerField(attribute="session_id")
    asset = fields.IntegerField(attribute="asset_id")
    duration_in_seconds = fields.FloatField(attribute="duration_in_seconds")

    class Meta:
        queryset = ListeningHistoryItem.objects.all()
        resource_name = "history"
        allowed_methods = ['get']
        serializer = PrettyJSONSerializer()
        filtering = {
            "duration": ('lte', 'gte'),
            "server_time"  : ('exact', 'gte', 'lte', 'range'),
            "session"  : ('exact'),
            "asset"  : ('exact'),
        }
