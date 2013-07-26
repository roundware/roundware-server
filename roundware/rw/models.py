from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from django.core.exceptions import NON_FIELD_ERRORS
from django.db import models, transaction
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from roundware.settings import MEDIA_BASE_URI
from roundware.rw import fields
from django.conf import settings
import datetime
from cache_utils.decorators import cached

try:
    import simplejson as json
except:
    import json

import logging

logger = logging.getLogger(name=__file__)


class Language(models.Model):
    language_code = models.CharField(max_length=10)

    def __unicode__(self):
            return str(self.id) + ": Language Code: " + self.language_code


class LocalizedString(models.Model):
    localized_string = models.TextField()
    language = models.ForeignKey(Language)

    def __unicode__(self):
            return str(self.id) + ": Language Code: " + self.language.language_code + ", String: " + self.localized_string


class RepeatMode(models.Model):
    mode = models.CharField(max_length=50)

    def __unicode__(self):
        return str(self.id) + ": " + self.mode


class Project(models.Model):
    name = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
    pub_date = models.DateTimeField('date published')
    audio_format = models.CharField(max_length=50)
    auto_submit = models.BooleanField()
    max_recording_length = models.IntegerField()
    listen_questions_dynamic = models.BooleanField()
    speak_questions_dynamic = models.BooleanField()
    sharing_url = models.CharField(max_length=512)
    sharing_message_loc = models.ManyToManyField(LocalizedString, related_name='sharing_msg_string', null=True, blank=True)
    out_of_range_message_loc = models.ManyToManyField(LocalizedString, related_name='out_of_range_msg_string', null=True, blank=True)
    out_of_range_url = models.CharField(max_length=512)
    recording_radius = models.IntegerField(null=True)
    listen_enabled = models.BooleanField()
    geo_listen_enabled = models.BooleanField()
    speak_enabled = models.BooleanField()
    geo_speak_enabled = models.BooleanField()
    reset_tag_defaults_on_startup = models.BooleanField()
    legal_agreement_loc = models.ManyToManyField(LocalizedString, related_name='legal_agreement_string', null=True, blank=True)
    repeat_mode = models.ForeignKey(RepeatMode, null=True)
    files_url = models.CharField(max_length=512, blank=True)
    files_version = models.CharField(max_length=16, blank=True)
    BITRATE_CHOICES = (
        ('64', '64'), ('96', '96'), ('112', '112'), ('128', '128'), ('160', '160'), ('192', '192'), ('256', '256'), ('320','320'),
    )
    audio_stream_bitrate = models.CharField(max_length=3, choices=BITRATE_CHOICES, default='128')
    ordering = models.CharField(max_length=16, choices=[('by_like', 'by_like'), ('by_weight', 'by_weight'), ('random', 'random')], default='random')
    demo_stream_enabled = models.BooleanField()
    demo_stream_url = models.CharField(max_length=512, blank=True)
    demo_stream_message_loc = models.ManyToManyField(LocalizedString, related_name='demo_stream_msg_string', null=True, blank=True)

    def __unicode__(self):
            return self.name

    @cached(60*60)
    def get_tag_cats_by_ui_mode(self, ui_mode):
        """ Return TagCategories for this project for specified UIMode 
            by name, like 'listen' or 'speak'.
            Pass name of UIMode.
        """
        logging.debug('inside get_tag_cats_by_ui_mode... not from cache')
        master_uis = MasterUI.objects.select_related('tag_category').filter(project=self, ui_mode__name=ui_mode)
        return [mui.tag_category for mui in master_uis]


    class Meta:
        permissions = (('access_project', 'Access Project'),)


class Session(models.Model):
    device_id = models.CharField(max_length=36, null=True, blank=True)
    starttime = models.DateTimeField()
    stoptime = models.DateTimeField(null=True, blank=True)
    project = models.ForeignKey(Project)
    ordering = ['id']
    language = models.ForeignKey(Language, null=True)
    client_type = models.CharField(max_length=128, null=True, blank=True)
    client_system = models.CharField(max_length=128, null=True, blank=True)
    demo_stream_enabled = models.BooleanField(default=False)

    def __unicode__(self):
        return str(self.id)


class UIMode(models.Model):
    name = models.CharField(max_length=50)
    data = models.TextField(null=True, blank=True)

    def __unicode__(self):
            return str(self.id) + ":" + self.name


class TagCategory(models.Model):
    name = models.CharField(max_length=50)
    data = models.TextField(null=True, blank=True)

    def __unicode__(self):
            return str(self.id) + ":" + self.name


class SelectionMethod(models.Model):
    name = models.CharField(max_length=50)
    data = models.TextField(null=True, blank=True)

    def __unicode__(self):
            return str(self.id) + ":" + self.name


class Tag(models.Model):
    tag_category = models.ForeignKey(TagCategory)
    value = models.TextField()
    description = models.TextField()
    loc_msg = models.ManyToManyField(LocalizedString, null=True, blank=True)
    data = models.TextField(null=True, blank=True)
    relationships = models.ManyToManyField('self', symmetrical=True, related_name='related_to', null=True, blank=True)

    def get_loc(self):
        return "<br />".join(unicode(t) for t in self.loc_msg.all())
    get_loc.short_description = "Localized Names"
    get_loc.name = "Localized Names"
    get_loc.allow_tags = True
    def get_relationships(self):
        return [rel['pk'] for rel in self.relationships.all().values('pk')]

    def __unicode__(self):
            return self.tag_category.name + " : " + self.description


class MasterUI(models.Model):
    name = models.CharField(max_length=50)
    header_text_loc = models.ManyToManyField(LocalizedString, null=True, blank=True)
    ui_mode = models.ForeignKey(UIMode)
    tag_category = models.ForeignKey(TagCategory)
    select = models.ForeignKey(SelectionMethod)
    active = models.BooleanField(default=True)
    index = models.IntegerField()
    project = models.ForeignKey(Project)

    def get_header_text_loc(self):
        return "<br />".join(unicode(t) for t in self.header_text_loc.all())
    get_header_text_loc.short_description = "Localized Header Text"
    get_header_text_loc.name = "Localized Header Text"
    get_header_text_loc.allow_tags = True

    def toTagDictionary(self):
        return {'name': self.name, 'code': self.tag_category.name, 'select': self.select.name, 'order': self.index}

    def save(self):
        # invalidate cached value for tag categories by ui_mode for the 
        # associated project.
        logging.debug("invalidating Project.get_tags_by_ui_mode for project "
                     " %s and UIMode %s" %(self.project, self.ui_mode.name))
        super(MasterUI, self).save()
        Project.get_tag_cats_by_ui_mode.invalidate(self.project, str(self.ui_mode.name))

    def __unicode__(self):
            return str(self.id) + ":" + self.ui_mode.name + ":" + self.name


class UIMapping(models.Model):
    master_ui = models.ForeignKey(MasterUI)
    index = models.IntegerField()
    tag = models.ForeignKey(Tag)
    default = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    #def toTagDictionary(self):
        #return {'tag_id':self.tag.id,'order':self.index,'value':self.tag.value}

    def __unicode__(self):
            return str(self.id) + ":" + self.master_ui.name + ":" + self.tag.tag_category.name


class Audiotrack(models.Model):
    project = models.ForeignKey(Project)
    minvolume = models.FloatField()
    maxvolume = models.FloatField()
    minduration = models.FloatField()
    maxduration = models.FloatField()
    mindeadair = models.FloatField()
    maxdeadair = models.FloatField()
    minfadeintime = models.FloatField()
    maxfadeintime = models.FloatField()
    minfadeouttime = models.FloatField()
    maxfadeouttime = models.FloatField()
    minpanpos = models.FloatField()
    maxpanpos = models.FloatField()
    minpanduration = models.FloatField()
    maxpanduration = models.FloatField()
    repeatrecordings = models.BooleanField()

    def norm_minduration(self):
        if self.minduration:
            return "%.2f s" % (self.minduration / 1000000000.0,)
    norm_minduration.short_description = "Min Duration"
    norm_minduration.name = "Min Duration"

    def norm_maxduration(self):
        if self.maxduration:
            return "%.2f s" % (self.maxduration / 1000000000.0,)
    norm_maxduration.short_description = "Max Duration"
    norm_maxduration.name = "Max Duration"

    def norm_mindeadair(self):
        if self.mindeadair:
            return "%.2f s" % (self.mindeadair / 1000000000.0,)
    norm_mindeadair.short_description = "Min Silence"
    norm_mindeadair.name = "Min Silence"

    def norm_maxdeadair(self):
        if self.maxdeadair:
            return "%.2f s" % (self.maxdeadair / 1000000000.0,)
    norm_maxdeadair.short_description = "Max Silence"
    norm_maxdeadair.name = "Max Silence"

    def __unicode__(self):
            return "Track " + str(self.id)


class EventType(models.Model):
    name = models.CharField(max_length=50)
    ordering = ['id']


class Event(models.Model):
    server_time = models.DateTimeField()
    client_time = models.CharField(max_length=50, null=True, blank=True)
    session = models.ForeignKey(Session)

    event_type = models.CharField(max_length=50)
    data = models.TextField(null=True, blank=True)
    latitude = models.CharField(max_length=50, null=True, blank=True)
    longitude = models.CharField(max_length=50, null=True, blank=True)
    tags = models.TextField(null=True, blank=True)

    operationid = models.IntegerField(null=True, blank=True)
    udid = models.CharField(max_length=50, null=True, blank=True)

#from south.modelsinspector import add_introspection_rules
#add_introspection_rules([], ["^roundware\.rw\.widgets\.LocationField"])

class Asset(models.Model):
    ASSET_MEDIA_TYPES = [('audio', 'audio'), ('video', 'video'),
                        ('photo', 'photo'), ('text', 'text')]
    MEDIATYPE_CONTENT_TYPES = {
        'audio': settings.ALLOWED_AUDIO_MIME_TYPES,
        'video': [],
        'photo': settings.ALLOWED_IMAGE_MIME_TYPES,
        'text': settings.ALLOWED_TEXT_MIME_TYPES,
    }
                        
    session = models.ForeignKey(Session, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=False)
    longitude = models.FloatField(null=True, blank=False)
    filename = models.CharField(max_length=256, null=True, blank=True)
    file = fields.RWValidatedFileField(storage=FileSystemStorage(
        location=getattr(settings, "MEDIA_BASE_DIR"),
        base_url=getattr(settings, "MEDIA_BASE_URI"),),
        content_types=getattr(settings,"ALLOWED_MIME_TYPES"),
        upload_to=".", help_text="Upload file")
    volume = models.FloatField(null=True, blank=True, default=1.0)

    submitted = models.BooleanField(default=True)
    project = models.ForeignKey(Project, null=True, blank=False)

    created = models.DateTimeField(default=datetime.datetime.now)
    audiolength = models.BigIntegerField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, null=True, blank=True)
    language = models.ForeignKey(Language, null=True)
    weight = models.IntegerField(choices=[(i, i) for i in range(0, 100)], default=50)
    mediatype = models.CharField(max_length=16, choices=ASSET_MEDIA_TYPES, default='audio')
    description = models.TextField(max_length=2048, blank=True)

    # enables inline adding/editing of Assets in Envelope Admin.
    # creates a relationship of an Asset to the Envelope, in which it was
    # initially added
    initialenvelope = models.ForeignKey('Envelope', null=True)

    tags.tag_category_filter = True

    audiolength.audio_length_filter = True

    def __init__(self, *args, **kwargs):
        super(Asset, self).__init__(*args, **kwargs)
        self.ENVELOPE_ID = 0

    def clean_fields(self, exclude=None):
        super(Asset, self).clean_fields(exclude)
        if not self.file:
            return
        # if this is first upload, file will have content_type that should
        # be validated
        if hasattr(self.file.file, 'content_type'):
            self.validate_filetype_for_mediatype(self.file.file.content_type)

    def validate_filetype_for_mediatype(self, content_type):
        """ content_type of file uploaded must be valid for mediatype 
        selected.  For now, just trusts the content_type coming through HTTP.  
        To be sure would need to examine the file. 
        """
        if content_type not in self.MEDIATYPE_CONTENT_TYPES[self.mediatype]:
            raise ValidationError(
                {
                    NON_FIELD_ERRORS:
                    (u"File type %s not supported for asset mediatype %s"
                    % (content_type, self.mediatype),)
                }   
            )

    def media_display(self):
        """display the media with HTML based on mediatype.
        """
        if self.mediatype == 'audio':
            return self.audio_player()
        elif self.mediatype == 'photo':
            return self.image_display()
        elif self.mediatype == 'text':
            return self.text_display()
        else:
            return ""
    media_display.short_name = "media"
    media_display.allow_tags = True

    def audio_player(self):
        if self.mediatype == 'audio':
            return """<div data-filename="%s" class="media-display audio-file"></div>""" % self.filename
    audio_player.short_name = "audio"
    audio_player.allow_tags = True

    def image_display(self):
        image_src = "%s%s" % (MEDIA_BASE_URI, self.filename)
        return """<div data-filename="%s" class="media-display image-file"><a href="%s" target="imagepop"
               ><img src="%s" alt="%s" title="%s"/></a></div>""" % (
                self.filename, image_src, image_src, 
                self.description, "click for full image")
    image_display.short_name = "image"
    image_display.allow_tags = True

    def text_display(self):
        try:
            fileread = self.file.read()
            self.file.close()
            chars = len(fileread)
            excerpt = fileread[:1000]
            more_str = chars > 1000 and """ <br/>... (excerpted from %s)""" % self.media_link_url() or ""
            return """<div data-filename="%s" class="media-display text-file"
                   >%s %s</div>""" % (self.filename, excerpt, more_str)
        except Exception as e:
           return """<div class="media-display" data-filename="%s">""" + '%s (%s)' % (self.filename, e.message, type(e)) + """</div>"""
    text_display.short_name = "text"
    text_display.allow_tags = True

    def location_map(self):
        html = """<input type="text" value="" id="searchbox" style=" width:700px;height:30px; font-size:15px;">
        <div id="map_instructions">To change or select location, type an address above and select from the available options;
        then move pin to exact location of asset.</div>
        <div class="GMap" id="map" style="width:800px; height: 600px; margin-top: 10px;"></div>""" # height 600
        return html
    location_map.short_name = "location"
    location_map.allow_tags = True

    def norm_audiolength(self):
        if self.audiolength:
            return "%.2f s" % (self.audiolength / 1000000000.0,)
    norm_audiolength.short_description = "Audio Length"
    norm_audiolength.name = "Audio Length"
    norm_audiolength.allow_tags = True

    def media_link_url(self):
        return '<a href="%s%s" target="_new">%s</a>' % (MEDIA_BASE_URI, self.filename, self.filename)
    media_link_url.allow_tags = True

    def get_tags(self):
        return "<br />".join(unicode(t) for t in self.tags.all())

    get_tags.short_description = "Tags"
    get_tags.name = "Tags"
    get_tags.allow_tags = True

    def get_flags(self):
        return self.vote_set.filter(type__iexact="flag").count()

    def get_likes(self):
        return self.vote_set.filter(type__iexact="like").count()

    #get_flags.admin_order_field = "vote"
    get_flags.short_description = "Flags"
    get_flags.name = "Flags"

    #get_likes.admin_order_field = "vote"
    get_likes.short_description = "Likes"
    get_likes.name = "Likes"

    def get_votes(self, dict=False):
        votes = self.vote_set.all()
        votes_dict = {}
        for v in votes:
            dict_num = votes_dict.get(v.type, 0)
            if v.value is None:
                value = 0
            else:
                value = v.value
            t_dict = {v.type: dict_num + value}
            votes_dict.update(t_dict)
        if dict:
            return votes_dict
        return ", ".join("%s : %d" % (v, num) for v, num in votes_dict.items())

    get_votes.short_description = "Votes"
    get_votes.name = "Votes"

    @transaction.commit_on_success
    def save(self, force_insert=False, force_update=False, using=None, *args, **kwargs):
        super(Asset, self).save(force_insert, force_update, using, *args, **kwargs)

    def __unicode__(self):
        return str(self.id) + ": " + self.mediatype + " at " + str(self.latitude) + "/" + str(self.longitude)


def get_default_session():
    return Session.objects.get(id=settings.DEFAULT_SESSION_ID)


class Envelope(models.Model):
    session = models.ForeignKey(Session, default=get_default_session)
    created = models.DateTimeField(default=datetime.datetime.now)
    assets = models.ManyToManyField(Asset, blank=True)

    def __unicode__(self):
            return str(self.id) + ": Session id: " + str(self.session.id)


class Speaker(models.Model):
    project = models.ForeignKey(Project)
    activeyn = models.BooleanField()
    code = models.CharField(max_length=10)
    latitude = models.FloatField()
    longitude = models.FloatField()
    maxdistance = models.IntegerField()
    mindistance = models.IntegerField()
    maxvolume = models.FloatField()
    minvolume = models.FloatField()
    uri = models.URLField()
    backupuri = models.URLField()

    def __unicode__(self):
            return str(self.id) + ": " + str(self.latitude) + "/" + str(self.longitude) + " : " + self.uri

    def location_map(self):
        html = """<input type="text" value="" id="searchbox" style=" width:700px;height:30px; font-size:15px;">
        <div id="map_instructions">To change or select location, type an address above and select from the available options;
        then move pin to exact location of asset.</div>
        <div id="map" style="width:800px; height: 600px; margin-top: 10px;"></div>"""
        return html
    location_map.short_name = "location"
    location_map.allow_tags = True

class ListeningHistoryItem(models.Model):
    session = models.ForeignKey(Session)
    asset = models.ForeignKey(Asset)
    starttime = models.DateTimeField()
    duration = models.BigIntegerField(null=True, blank=True)

    def norm_duration(self):
        if self.duration:
            return "%.2f s" % (self.duration / 1000000000.0,)
    norm_duration.short_description = "Playback Duration"
    norm_duration.name = "Playback Duration"

    def __unicode__(self):
            return str(self.id) + ": Session id: " + str(self.session.id) + ": Asset id: " + str(self.asset.id) + " duration: " + str(self.duration)


class Vote(models.Model):
    value = models.IntegerField(null=True, blank=True)
    session = models.ForeignKey(Session)
    asset = models.ForeignKey(Asset)
    type = models.CharField(max_length=16, choices=[('like', 'like'), ('flag', 'flag')])

    def __unicode__(self):
            return str(self.id) + ": Session id: " + str(self.session.id) + ": Asset id: " + str(self.asset.id) + ": Value: " + str(self.value)


def get_field_names_from_model(model):
    """Pass in a model class. Return list of strings of field names"""
    return [f.name for f in model._meta.fields]


