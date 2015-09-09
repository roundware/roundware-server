# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from guardian.admin import GuardedModelAdmin
from guardian.shortcuts import get_objects_for_user
from models import *
from django.contrib import admin

from roundware.rw.admin_helper import add_asset_to_envelope, create_envelope
from roundware.rw.filters import AudiolengthListFilter, TagCategoryListFilter


class VoteInline(admin.TabularInline):
    model = Vote
    extra = 1


class EnvelopeInline(admin.StackedInline):
    model = Envelope.assets.through
    extra = 0
    can_delete = False
    verbose_name = ""
    verbose_name_plural = "Related Envelope"


class TimedAssetInline(admin.TabularInline):
    model = TimedAsset
    extra = 1


class AssetTagsInline(admin.TabularInline):
    model = Asset.tags.through


class SmarterModelAdmin(admin.ModelAdmin):
    valid_lookups = ()

    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup.startswith(self.valid_lookups):
            return True
        return super(SmarterModelAdmin, self).lookup_allowed(lookup, *args, **kwargs)


def project_restricted_queryset_through(model_class, field_name):
    """
    Returns a ModelAdmin queryset function that filters out objects not linked
    to a project through model_class (referred to in the model by field_name)
    on which request.user has the access_project permission

    ex:

    project_restricted_queryset_through(Asset, 'asset') provide the filter
    original_queryset.filter(asset__in=Asset.objects.filter(project__in=accessible_projects)
    """

    def get_queryset(self, request):
        qset = super(admin.ModelAdmin, self).get_queryset(request)

        if request.user.is_superuser:
            return qset

        accessible_projects = get_objects_for_user(
            request.user, 'rw.access_project')
        authorized_objects = model_class.objects.filter(
            project__in=accessible_projects)
        return qset.filter(**{field_name + "__in": authorized_objects})
    return get_queryset


class ProjectProtectedThroughAssetModelAdmin(admin.ModelAdmin):
    queryset = project_restricted_queryset_through(Asset, 'asset')


class ProjectProtectedThroughSessionModelAdmin(admin.ModelAdmin):
    queryset = project_restricted_queryset_through(Session, 'session')


class ProjectProtectedThroughUIModelAdmin(admin.ModelAdmin):
    queryset = project_restricted_queryset_through(MasterUI, 'master_ui')


class ProjectProtectedModelAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qset = super(admin.ModelAdmin, self).get_queryset(request)

        if request.user.is_superuser:
            return qset

        return qset.filter(project__in=get_objects_for_user(request.user, 'rw.access_project'))


def copy_asset(modeladmin, request, queryset):
    for obj in queryset:
        tags = obj.tags.all()
        obj.pk = None
        obj.save()
        for i in tags:
            obj.tags.add(i)
copy_asset.short_description = "Copy selected assets"

def copy_asset_with_votes(modeladmin, request, queryset):
    for obj in queryset:
        tags = obj.tags.all()
        votes = obj.vote_set.all()
        obj.pk = None
        obj.save()
        for i in tags:
            obj.tags.add(i)
        for i in votes:
            obj.vote_set.add(i)
copy_asset_with_votes.short_description = "Copy selected assets while retaining votes"

class AssetAdmin(ProjectProtectedModelAdmin):
    valid_lookups = ('tags__tag_category__name', 'tags__description')

    # In order for the audio file server URI to be stored in settings,
    # we need custom views and templates
    # Template is reused, file to extend is passed as a parameter
    change_form_template = "admin/asset_change_form.html"
    change_list_template = "admin/asset_change_form.html"

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['MEDIA_URL'] = settings.MEDIA_URL
        extra_context['extends_url'] = "admin/change_form.html"
        return super(AssetAdmin, self).add_view(request, form_url, extra_context=extra_context)

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context['MEDIA_URL'] = settings.MEDIA_URL
        extra_context['extends_url'] = "admin/change_form.html"
        return super(AssetAdmin, self).change_view(request, object_id, extra_context=extra_context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['MEDIA_URL'] = settings.MEDIA_URL
        extra_context['extends_url'] = "admin/change_list.html"
        return super(AssetAdmin, self).changelist_view(request, extra_context=extra_context)

    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup.startswith(self.valid_lookups):
            return True
        return super(AssetAdmin, self).lookup_allowed(lookup, *args, **kwargs)

    def save_model(self, request, obj, form, change):
        # only call create_envelope if the model is being added.
        if not change:
            create_envelope(instance=obj)
        obj.save()

        # only call add_asset_to_envelope when the model is being added.
        if not change:
            add_asset_to_envelope(instance=obj)

    actions = [copy_asset, copy_asset_with_votes]
    actions_on_bottom = True
    ordering = ['-id']
    # save_as = True
    list_per_page = 25
    inlines = [
        EnvelopeInline,
        VoteInline,
        TimedAssetInline,
    ]
    #exclude = ('tags',)
    # , 'longitude', 'latitude')#, 'filename')
    readonly_fields = ('location_map', 'audio_player',
                       'media_display', 'audiolength', 'session', 'created')
    list_display = ('id', 'session', 'submitted', 'project', 'media_link_url', 'mediatype', 'audio_player', 'created',
                    'norm_audiolength', 'get_likes', 'get_flags', 'get_tags', 'weight', 'volume', )
    list_filter = ('project', 'submitted', 'mediatype', 'created', 'language',
                   ('audiolength', AudiolengthListFilter), ('tags', TagCategoryListFilter))
    list_editable = ('submitted', 'weight', 'volume')
    save_on_top = True
    filter_horizontal = ('tags', 'loc_description')
    fieldsets = (
        ('Media Data', {
            'fields': (
                'mediatype',
                'media_display',
                'file',
                'volume',
                'audiolength',
                'description',
                'loc_description'
            )
        }),
        (None, {
            'fields': (
                'project',
                'language',
                'session',
                'created',
                'weight',
                'submitted',
                'tags'
            )
        }),
        ('Geographical Data', {
            'fields': (
                'location_map',
                'longitude',
                'latitude'
            )
        })
    )

    class Media:
        css = {
            "all": (
                "rw/css/jplayer.blue.monday.css",
                "http://code.jquery.com/ui/1.10.3/themes/smoothness/jquery-ui.css",
                "rw/css/asset_admin.css"
            )
        }
        js = (
            'rw/js/jquery.jplayer.min.js',
            'rw/js/audio.js',
            'http://maps.google.com/maps/api/js?sensor=false',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/jquery-ui.min.js',
            'rw/js/location_map.js',
            'rw/js/asset_admin.js',
        )


class AssetInline(admin.StackedInline):
    model = Asset
    verbose_name_plural = "Add/edit Assets (click Asset header to show fields)"
    # ct_field = "dj_content_type"
    extra = 0
    fieldsets = AssetAdmin.fieldsets
    readonly_fields = AssetAdmin.readonly_fields
    filter_horizontal = ('tags',)
    # prepopulated_fields = {"session": ("title",)}


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag_category', 'value', 'get_loc')
    search_fields = ('description',)
    list_filter = ('tag_category',)
    ordering = ['id']
    filter_vertical = ('loc_msg', 'loc_description')
    filter_horizontal = ('relationships',)
    # inlines = [
    #    AssetTagsInline,
    # ]
    change_list_template = 'admin/tag_change_list.html'


class LanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'language_code')
    ordering = ['id']


class LocalizedStringAdmin(admin.ModelAdmin):
    list_display = ('id', 'language', 'localized_string')
    ordering = ['id']
    list_filter = ('language',)
    search_fields = ('localized_string',)


class VoteAdmin(ProjectProtectedThroughAssetModelAdmin):
    list_display = ('id', 'session', 'asset', 'value')
    ordering = ['id']


class ProjectAdmin(GuardedModelAdmin):
    list_display = ('id', 'name', 'latitude', 'longitude',
                    'max_recording_length', 'recording_radius')
    ordering = ['id']
    save_on_top = True
    filter_vertical = ('sharing_message_loc', 'out_of_range_message_loc', 'legal_agreement_loc',
                       'demo_stream_message_loc')
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'latitude', 'longitude', 'pub_date', 'auto_submit')
        }),
        ('Configuration', {
            'fields': ('listen_enabled', 'geo_listen_enabled', 'speak_enabled', 'geo_speak_enabled',
                       'demo_stream_enabled', 'reset_tag_defaults_on_startup', 'timed_asset_priority',
                       'max_recording_length', 'recording_radius', 'audio_stream_bitrate', 'sharing_url',
                       'out_of_range_url', 'demo_stream_url', 'files_url', 'files_version', 'repeat_mode', 'ordering')
        }),
        ('Localized Strings', {
            'fields': ('sharing_message_loc', 'out_of_range_message_loc', 'legal_agreement_loc',
                       'demo_stream_message_loc')
        }),
        ('Other', {
            'classes': ('collapse',),
            'fields': ('audio_format', 'listen_questions_dynamic', 'speak_questions_dynamic')
        }),
    )


class SessionAdmin(ProjectProtectedModelAdmin):
    list_display = ('id', 'project', 'starttime', 'device_id', 'language')
    list_filter = ('project', 'language', 'starttime')
    ordering = ['-id']


class TagCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'data')
    ordering = ['id']


# MasterUIs describe screens containing choices limited to one mode (Speak, Listen),
#  and one tag category.
class MasterUIAdmin(ProjectProtectedModelAdmin):
    list_display = ('id', 'project', 'name', 'get_header_text_loc',
                    'ui_mode', 'tag_category', 'select', 'active', 'index')
    list_filter = ('project', 'ui_mode', 'tag_category')
    ordering = ['id']
    filter_horizontal = ('header_text_loc', )
    save_as = True


# UI Mappings describe the ordering and selectability of tags for a given
# MasterUI.
class UIMappingAdmin(ProjectProtectedThroughUIModelAdmin):
    list_display = ('id', 'active', 'master_ui', 'index', 'tag', 'default')
    list_filter = ('master_ui',)
    list_editable = ('active', 'default', 'index')
    ordering = ['id']
    save_as = True


class AudiotrackAdmin(ProjectProtectedModelAdmin):
    list_display = ('id', 'project', 'norm_minduration',
                    'norm_maxduration', 'norm_mindeadair', 'norm_maxdeadair')
    list_filter = ('project',)
    ordering = ['id']
    save_as = True
    fieldsets = (
        (None, {
            'fields': ('project', 'minvolume', 'maxvolume')
        }),
        ('Chunks', {
            'fields': ('minduration', 'maxduration', 'mindeadair', 'maxdeadair')
        }),
        ('Fading', {
            'fields': ('minfadeintime', 'maxfadeintime', 'minfadeouttime', 'maxfadeouttime')
        }),
        ('Panning', {
            'fields': ('minpanpos', 'maxpanpos', 'minpanduration', 'maxpanduration')
        }),
    )


class EventAdmin(ProjectProtectedThroughSessionModelAdmin):
    list_display = (
        'id', 'session', 'event_type', 'latitude', 'longitude', 'data', 'server_time')
    # search_fields = ('session',)
    list_filter = ('event_type', 'server_time')
    ordering = ['-id']


class EnvelopeAdmin(ProjectProtectedThroughSessionModelAdmin):
    list_display = ('id', 'session', 'created')
    ordering = ['-id']
    inlines = [AssetInline, ]
    filter_horizontal = ('assets',)
    readonly_fields = ('session',)

    def save_formset(self, request, form, formset, change):
        """
        Given an inline formset save it to the database.
        """
        def set_session(instance):
            if not instance.session:
                instance.session = form.cleaned_data['session']
            instance.save()

        def add_to_envelope(instance):
            instance.ENVELOPE_ID = formset.instance.id
            add_asset_to_envelope(instance=instance)

        logger.debug("Saving envelope")

        if formset.model == Asset:
            instances = formset.save(commit=False)
            map(set_session, instances)
            map(add_to_envelope, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()

    class Media:
        js = (
            'http://maps.google.com/maps/api/js?sensor=false',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/jquery-ui.min.js',
            'rw/js/location_map.js',
            'rw/js/asset_admin.js',
            'rw/js/envelope_admin.js',
        )

        css = {
            "all": (
                "rw/css/jplayer.blue.monday.css",
                "http://code.jquery.com/ui/1.10.3/themes/smoothness/jquery-ui.css",
                "rw/css/asset_admin.css",
                "rw/css/envelope_admin.css"
            )
        }


class SpeakerAdmin(ProjectProtectedModelAdmin):
    readonly_fields = ('location_map',)
    list_display = ('id', 'activeyn', 'code', 'project', 'latitude',
                    'longitude', 'maxdistance', 'mindistance', 'maxvolume', 'minvolume', 'uri')
    list_filter = ('project', 'activeyn')
    list_editable = (
        'activeyn', 'maxdistance', 'mindistance', 'maxvolume', 'minvolume',)
    ordering = ['id']
    save_as = True
    save_on_top = True

    fieldsets = (
        (None, {
         'fields': ('activeyn', 'code', 'project', 'maxvolume', 'minvolume', 'uri')}),
        ('Geographical Data', {'fields': (
            'location_map', 'longitude', 'latitude', 'maxdistance', 'mindistance')})
    )

    class Media:
        css = {
            "all": (
                "http://code.jquery.com/ui/1.10.3/themes/smoothness/jquery-ui.css",
            )
        }
        js = (
            'http://maps.google.com/maps/api/js?sensor=false',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/jquery-ui.min.js',
            'rw/js/location_map.js',
        )


class ListeningHistoryItemAdmin(ProjectProtectedThroughAssetModelAdmin):
    list_display = ('id', 'session', 'asset', 'starttime', 'norm_duration')
    ordering = ['session']


class TimedAssetAdmin(ProjectProtectedModelAdmin):
    list_display = ('id', 'project', 'asset', 'start', 'end')
    ordering = ['id']
    list_filter = ('project__name',)


admin.site.register(Language, LanguageAdmin)
admin.site.register(LocalizedString, LocalizedStringAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Audiotrack, AudiotrackAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(TagCategory, TagCategoryAdmin)
admin.site.register(MasterUI, MasterUIAdmin)
admin.site.register(UIMapping, UIMappingAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Speaker, SpeakerAdmin)
admin.site.register(Envelope, EnvelopeAdmin)
admin.site.register(ListeningHistoryItem, ListeningHistoryItemAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(TimedAsset, TimedAssetAdmin)
