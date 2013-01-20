from roundware.geoposition.forms import GeopositionField
from guardian.admin import GuardedModelAdmin
from guardian.shortcuts import get_objects_for_user
from models import *
from django.contrib import admin
from django import forms
from settings import AUDIO_FILE_URI

from filterspec import TagCategoryFilterSpec, AudioLengthFilterSpec


class VoteInline(admin.TabularInline):
    model = Vote


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
    def queryset(self, request):
        qset = super(admin.ModelAdmin, self).queryset(request)

        if request.user.is_superuser:
            return qset

        accessible_projects = get_objects_for_user(request.user, 'rw.access_project')
        authorized_objects = model_class.objects.filter(project__in=accessible_projects)
        return qset.filter(**{field_name + "__in": authorized_objects})
    return queryset


class ProjectProtectedThroughAssetModelAdmin(admin.ModelAdmin):
    queryset = project_restricted_queryset_through(Asset, 'asset')


class ProjectProtectedThroughSessionModelAdmin(admin.ModelAdmin):
    queryset = project_restricted_queryset_through(Session, 'session')


class ProjectProtectedThroughUIModelAdmin(admin.ModelAdmin):
    queryset = project_restricted_queryset_through(MasterUI, 'master_ui')


class ProjectProtectedModelAdmin(admin.ModelAdmin):
    def queryset(self, request):
        qset = super(admin.ModelAdmin, self).queryset(request)

        if request.user.is_superuser:
            return qset

        return qset.filter(project__in=get_objects_for_user(request.user, 'rw.access_project'))


class AssetAdminForm(forms.ModelForm):
    # Step 1: Add the extra form fields to the ModelForm
    #latitude = forms.FloatField(required=False)
    #longitude = forms.FloatField(required=False)
    map = GeopositionField()

    class Meta:
        model = Asset

    # Step 2: Override the constructor to manually set the form's latitude and
    # longitude fields if a Location instance is passed into the form
    def __init__(self, *args, **kwargs):
        super(AssetAdminForm, self).__init__(*args, **kwargs)
        self.initial['map'] = (self.instance.latitude, self.instance.longitude)

    # Step 3: Override the save method to manually set the model's latitude and
    # longitude properties based on what was submitted from the form
    def save(self, commit=True):
        model = super(AssetAdminForm, self).save(commit=False)
        #
        # Save the latitude and longitude based on the form fields
        model.latitude = float(self.cleaned_data['map'][0])
        model.longitude = float(self.cleaned_data['map'][1])

        if commit:
            model.save()

        return model


class AssetAdmin(ProjectProtectedModelAdmin):
    valid_lookups = ('tags__tag_category__name', 'tags__description')

    # In order for the audio file server URI to be stored in settings,
    # we need custom views and templates
    # Template is reused, file to extend is passed as a parameter
    change_form_template = "admin/asset_change_form.html"
    change_list_template = "admin/asset_change_form.html"

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['AUDIO_FILE_URI'] = AUDIO_FILE_URI
        extra_context['extends_url'] = "admin/change_form.html"
        return super(AssetAdmin, self).add_view(request, form_url,
            extra_context=extra_context)

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context['AUDIO_FILE_URI'] = AUDIO_FILE_URI
        extra_context['extends_url'] = "admin/change_form.html"
        return super(AssetAdmin, self).change_view(request, object_id,
            extra_context=extra_context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['AUDIO_FILE_URI'] = AUDIO_FILE_URI
        extra_context['extends_url'] = "admin/change_list.html"
        return super(AssetAdmin, self).changelist_view(request,
            extra_context=extra_context)

    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup.startswith(self.valid_lookups):
            return True
        return super(AssetAdmin, self).lookup_allowed(lookup, *args, **kwargs)

    form = AssetAdminForm

    ordering = ['-id']
    inlines = [
        VoteInline,
    ]
    #exclude = ('tags',)
    readonly_fields = ('audio_player', 'audiolength', 'session', 'created', 'filename')
    list_display = ('id', 'session', 'submitted', 'project', 'audio_link_url', 'audio_player', 'created',
                    'norm_audiolength', 'get_likes', 'get_flags', 'get_tags', 'volume', )
    list_filter = ('project', 'tags', 'submitted', 'audiolength', 'created', 'language', )
    list_editable = ('submitted', 'volume')
    save_on_top = True
    filter_horizontal = ('tags',)

    class Media:
        css = {"all": ("css/jplayer.blue.monday.css",)}
        js = ('js/jquery.jplayer.min.js', 'js/audio.js')


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag_category', 'description', 'get_loc')
    search_fields = ('description',)
    list_filter = ('tag_category',)
    ordering = ['id']
    # inlines = [
    #    AssetTagsInline,
    # ]


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


class RepeatModeAdmin(admin.ModelAdmin):
    list_display = ('id', 'mode')
    ordering = ['id']


class ProjectAdmin(GuardedModelAdmin):
    list_display = ('id', 'name', 'latitude', 'longitude', 'max_recording_length', 'recording_radius')
    ordering = ['id']
    save_on_top = True
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'latitude', 'longitude', 'pub_date', 'audio_format', 'auto_submit')
        }),
        ('Configuration', {
            'fields': ('listen_enabled', 'geo_listen_enabled', 'speak_enabled', 'geo_speak_enabled',
                       'reset_tag_defaults_on_startup', 'max_recording_length', 'recording_radius', 'sharing_url',
                       'out_of_range_url', 'files_url', 'repeat_mode')
        }),
        ('Localized Strings', {
            'fields': ('sharing_message_loc', 'out_of_range_message_loc', 'legal_agreement_loc',)
        }),
        ('Other', {
            'classes': ('collapse',),
            'fields': ('new_recording_email_body', 'new_recording_email_recipient', 'listen_questions_dynamic',
                       'speak_questions_dynamic', 'sharing_message', 'out_of_range_message', 'legal_agreement')
        }),
        )


class SessionAdmin(ProjectProtectedModelAdmin):
    list_display = ('id', 'project', 'starttime', 'device_id', 'language')
    list_filter = ('project', 'language', 'starttime')
    ordering = ['-id']


class UIModeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'data')
    ordering = ['id']


class TagCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'data')
    ordering = ['id']


class SelectionMethodAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'data')
    ordering = ['id']


#MasterUIs describe screens containing choices limited to one mode (Speak, Listen),
#  and one tag category.
class MasterUIAdmin(ProjectProtectedModelAdmin):
    list_display = ('id', 'project', 'name', 'ui_mode', 'tag_category', 'select', 'active', 'index')
    list_filter = ('project', 'ui_mode', 'tag_category')
    ordering = ['id']


#UI Mappings describe the ordering and selectability of tags for a given MasterUI.
class UIMappingAdmin(ProjectProtectedThroughUIModelAdmin):
    list_display = ('id', 'active', 'master_ui', 'index', 'tag', 'default')
    list_filter = ('master_ui',)
    list_editable = ('active', 'default', 'index')
    ordering = ['id']


class AudiotrackAdmin(ProjectProtectedModelAdmin):
    list_display = ('id', 'project', 'norm_minduration', 'norm_maxduration', 'norm_mindeadair', 'norm_maxdeadair')
    list_filter = ('project',)
    ordering = ['id']
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
    list_display = ('id', 'session', 'event_type', 'latitude','longitude', 'data', 'server_time')
    # search_fields = ('session',)
    list_filter = ('event_type', 'server_time')
    ordering = ['id']


class EnvelopeAdmin(ProjectProtectedThroughSessionModelAdmin):
    list_display = ('id', 'session')
    ordering = ['id']


class SpeakerAdmin(ProjectProtectedModelAdmin):
    list_display = ('id', 'activeyn', 'code', 'project', 'latitude', 'longitude', 'maxdistance', 'mindistance', 'maxvolume', 'minvolume', 'uri')
    list_filter = ('project', 'activeyn')
    list_editable = ('activeyn', 'maxdistance', 'mindistance', 'maxvolume', 'minvolume',)
    ordering = ['id']


class ListeningHistoryItemAdmin(ProjectProtectedThroughAssetModelAdmin):
    list_display = ('id', 'session', 'asset', 'starttime', 'norm_duration')
    ordering = ['session']


admin.site.register(Language, LanguageAdmin)
admin.site.register(LocalizedString, LocalizedStringAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Audiotrack, AudiotrackAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(UIMode, UIModeAdmin)
admin.site.register(TagCategory, TagCategoryAdmin)
admin.site.register(MasterUI, MasterUIAdmin)
admin.site.register(UIMapping, UIMappingAdmin)
admin.site.register(SelectionMethod, SelectionMethodAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(EventType)
admin.site.register(Event, EventAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Speaker, SpeakerAdmin)
admin.site.register(Envelope, EnvelopeAdmin)
admin.site.register(ListeningHistoryItem, ListeningHistoryItemAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(RepeatMode, RepeatModeAdmin)
