# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.


from __future__ import unicode_literals
from django.contrib.gis.geos import Point
from django.core.cache import cache

cache # pyflakes, make sure it is imported, for patching in tests
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.exceptions import NON_FIELD_ERRORS
from django.db import transaction
from django.contrib.gis.db import models
from validatedfile.fields import ValidatedFileField
from django.conf import settings
from datetime import datetime
from cache_utils.decorators import cached
from django.db.models.signals import post_save
import logging
from geopy.distance import vincenty

logger = logging.getLogger(__name__)


class Asset(models.Model):
    """
    Individual piece of content
    """
    ASSET_MEDIA_TYPES = [('audio', 'audio'), ('video', 'video'),
                         ('photo', 'photo'), ('text', 'text')]
    MEDIATYPE_CONTENT_TYPES = {
        'audio': settings.ALLOWED_AUDIO_MIME_TYPES,
        'video': [],
        'photo': settings.ALLOWED_IMAGE_MIME_TYPES,
        'text': settings.ALLOWED_TEXT_MIME_TYPES,
    }

    class Meta:
        ordering = ['id']

    session = models.ForeignKey(
        'Session', null=True, blank=True)
    latitude = models.FloatField(null=True, blank=False)
    longitude = models.FloatField(null=True, blank=False)
    shape = models.MultiPolygonField(geography=True, null=True, blank=True)
    filename = models.CharField(max_length=256, null=True, blank=True)
    file = ValidatedFileField(storage=FileSystemStorage(
        location=settings.MEDIA_ROOT,
        base_url=settings.MEDIA_URL,),
        content_types=settings.ALLOWED_MIME_TYPES,
        upload_to=".", help_text="Upload file")
    volume = models.FloatField(null=True, blank=True, default=1.0)

    submitted = models.BooleanField(default=True)
    project = models.ForeignKey('Project', null=True, blank=False)

    created = models.DateTimeField(default=datetime.now)
    audiolength = models.BigIntegerField(null=True, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    language = models.ForeignKey('Language', null=True)
    weight = models.IntegerField(
        choices=[(i, i) for i in range(0, 100)], default=50)
    mediatype = models.CharField(
        max_length=16, choices=ASSET_MEDIA_TYPES, default='audio')
    description = models.TextField(max_length=2048, blank=True)
    loc_description = models.ManyToManyField(
        'LocalizedString', blank=True)
    loc_alt_text = models.ManyToManyField(
        'LocalizedString', blank=True, related_name='alt_text_string')

    # TODO: needs verification
    loc_caption = ValidatedFileField(storage=FileSystemStorage(
        location=settings.MEDIA_ROOT,
        base_url=settings.MEDIA_URL,),
        content_types=settings.ALLOWED_TEXT_MIME_TYPES,
        upload_to=".", help_text="Upload captions", null=True)

    # enables inline adding/editing of Assets in Envelope Admin.
    # creates a relationship of an Asset to the Envelope, in which it was
    # initially added
    initialenvelope = models.ForeignKey('Envelope', null=True)

    # no more FilterSpec in Django >= 1.4
    # tags.tag_category_filter = True
    # audiolength.audio_length_filter = True
    audiolength.verbose_name = 'audio file length'

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
        image_src = "%s%s" % (settings.MEDIA_URL, self.filename)
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
            more_str = chars > 1000 and """ <br/>... (excerpted from %s)""" % self.media_link_url(
            ) or ""
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
        <div class="GMap" id="map" style="width:800px; height: 600px; margin-top: 10px;"></div>"""  # height 600
        return html
    location_map.short_name = "location"
    location_map.allow_tags = True

    def norm_audiolength(self):
        if self.audiolength:
            return "%.2f s" % (self.audiolength / 1000000000.0,)

    def audiolength_in_seconds(self):
        if self.audiolength:
            return '%.2f' % round(self.audiolength / 1000000000.0, 2)
    norm_audiolength.short_description = "Audio Length"
    norm_audiolength.name = "Audio Length"
    norm_audiolength.allow_tags = True

    def media_link_url(self):
        return '<a href="%s%s" target="_new">%s</a>' % (settings.MEDIA_URL, self.filename, self.filename)
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

    # get_flags.admin_order_field = "vote"
    get_flags.short_description = "Flags"
    get_flags.name = "Flags"

    # get_likes.admin_order_field = "vote"
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

    def distance(self, listener):
        listener_location = (listener['latitude'], listener['longitude'])
        speaker_location = (self.latitude, self.longitude)
        return vincenty(listener_location, speaker_location)

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, using=None, *args, **kwargs):
        super(Asset, self).save(
            force_insert, force_update, using, *args, **kwargs)

    def __unicode__(self):
        return str(self.id) + ": " + self.mediatype + " at " + str(self.latitude) + "/" + str(self.longitude)


class Audiotrack(models.Model):
    """
    A linear assemblage of alternating audio Assets and silence
    that forms audio stream along with Speaker audio
    """
    project = models.ForeignKey('Project')
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
    repeatrecordings = models.BooleanField(default=False)

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


class Envelope(models.Model):
    """
    Entity for bundling Assets together
    """
    session = models.ForeignKey('Session', blank=True)
    created = models.DateTimeField(default=datetime.now)
    assets = models.ManyToManyField(Asset, blank=True)

    def __unicode__(self):
        return str(self.id) + ": Session id: " + str(self.session.id)


class Event(models.Model):
    """
    Record of user interactions with server
    """
    server_time = models.DateTimeField()
    client_time = models.CharField(max_length=50, null=True, blank=True)
    session = models.ForeignKey('Session')

    event_type = models.CharField(max_length=50)
    data = models.TextField(null=True, blank=True)
    latitude = models.CharField(max_length=50, null=True, blank=True)
    longitude = models.CharField(max_length=50, null=True, blank=True)
    tags = models.TextField(null=True, blank=True)


class Language(models.Model):
    """
    Defines what languages are available to Projects on server
    """
    name = models.CharField(max_length=20, blank=True)
    language_code = models.CharField(max_length=10)

    def __unicode__(self):
        return str(self.id) + ": Language: " + self.name


class ListeningHistoryItem(models.Model):
    """
    Tracks what Assets are played when in each Session
    """
    session = models.ForeignKey('Session')
    asset = models.ForeignKey(Asset)
    starttime = models.DateTimeField()
    duration = models.BigIntegerField(null=True, blank=True)

    def norm_duration(self):
        if self.duration:
            return "%.2f s" % (self.duration / 1000000000.0,)

    def duration_in_seconds(self):
        if self.duration:
            return '%.2f' % round(self.duration / 1000000000.0, 2)
    norm_duration.short_description = "Playback Duration"
    norm_duration.name = "Playback Duration"

    def __unicode__(self):
        return str(self.id) + ": Session id: " + str(self.session.id) + ": Asset id: " + str(self.asset.id) + " duration: " + str(self.duration)

    class Meta:
        verbose_name = 'Listening History Item'
        verbose_name_plural = 'Listening History Items'


class LocalizedString(models.Model):
    """
    A string and corresponding language.
    """
    localized_string = models.TextField()
    language = models.ForeignKey(Language)

    def __unicode__(self):
        return str(self.id) + ": Language: " + self.language.name + ", String: " + self.localized_string

    class Meta:
        verbose_name = 'Localized String'
        verbose_name_plural = 'Localized Strings'


class Project(models.Model):
    """
    The highest level of segmentation/grouping for all RW data.
    """
    BITRATES = (
        ('64', '64'),
        ('96', '96'),
        ('112', '112'),
        ('128', '128'),
        ('160', '160'),
        ('192', '192'),
        ('256', '256'),
        ('320', '320'),
    )
    STOP = 'stop'
    CONTINUOUS = 'continuous'
    REPEAT_MODES = (
        (STOP, 'stop'),
        (CONTINUOUS, 'continuous'),
    )

    name = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
    pub_date = models.DateTimeField('date published')
    languages = models.ManyToManyField(
        Language, related_name='languages', blank=False)
    audio_format = models.CharField(max_length=50)
    auto_submit = models.BooleanField(default=False)
    max_recording_length = models.IntegerField()
    listen_questions_dynamic = models.BooleanField(default=False)
    speak_questions_dynamic = models.BooleanField(default=False)
    sharing_url = models.CharField(max_length=512)
    sharing_message_loc = models.ManyToManyField(
        LocalizedString, related_name='sharing_msg_string', blank=True)
    out_of_range_message_loc = models.ManyToManyField(
        LocalizedString, related_name='out_of_range_msg_string', blank=True)
    out_of_range_url = models.CharField(max_length=512)
    recording_radius = models.IntegerField(null=True)
    listen_enabled = models.BooleanField(default=False)
    geo_listen_enabled = models.BooleanField(default=False)
    speak_enabled = models.BooleanField(default=False)
    geo_speak_enabled = models.BooleanField(default=False)
    reset_tag_defaults_on_startup = models.BooleanField(default=False)
    timed_asset_priority = models.BooleanField(default=True)
    legal_agreement_loc = models.ManyToManyField(
        LocalizedString, related_name='legal_agreement_string', blank=True)
    repeat_mode = models.CharField(default=STOP, max_length=10, blank=False,
                               choices=REPEAT_MODES)

    files_url = models.CharField(max_length=512, blank=True)
    files_version = models.CharField(max_length=16, blank=True)
    audio_stream_bitrate = models.CharField(
        max_length=3, choices=BITRATES, default='128')

    ordering_choices = [('by_like', 'by_like'),
                        ('by_weight', 'by_weight'),
                        ('random', 'random')]

    ordering = models.CharField(max_length=16, choices=ordering_choices, default='random')
    demo_stream_enabled = models.BooleanField(default=False)
    demo_stream_url = models.CharField(max_length=512, blank=True)
    demo_stream_message_loc = models.ManyToManyField(
        LocalizedString, related_name='demo_stream_msg_string', blank=True)

    out_of_range_distance = models.FloatField(default=1000)

    def __unicode__(self):
        return self.name

    def get_tag_cats_by_ui_mode(self, ui_mode):
        """ Return TagCategories for this project for specified UIGroup.mode
            by key UIGroup.SPEAK or UIGroup.LISTEN.
            UIGroup must be active
        """
        ui_groups = UIGroup.objects.select_related('tag_category').filter(
            project=self, ui_mode=ui_mode, active=True)
        return [uig.tag_category for uig in ui_groups]

    class Meta:
        permissions = (('access_project', 'Access Project'),)


class ProjectGroup(models.Model):
    """
    Method for grouping projects for transformer client
    """
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    description = models.TextField(max_length=2048, blank=True)
    projects = models.ManyToManyField(Project, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Project Group'
        verbose_name_plural = 'Project Groups'


class Session(models.Model):
    """
    A client server connection established when the client is started
    and terminated when the client app is closed.
    """
    device_id = models.CharField(max_length=36, null=True, blank=True)

    starttime = models.DateTimeField()
    stoptime = models.DateTimeField(null=True, blank=True)

    project = models.ForeignKey(Project)
    language = models.ForeignKey(Language, null=True)
    client_type = models.CharField(max_length=128, null=True, blank=True)
    client_system = models.CharField(max_length=128, null=True, blank=True)
    demo_stream_enabled = models.BooleanField(default=False)
    geo_listen_enabled = models.BooleanField(default=True)
    timezone = models.CharField(max_length=5, default="0000")

    def __unicode__(self):
        return str(self.id)


class Speaker(models.Model):
    """
    Define geographic polygons where specific audio streams are heard
    """

    def __init__(self, *args, **kwargs):
        super(Speaker, self).__init__(*args, **kwargs)
        self._shape_cache = self.shape
        self._attenuation_distance_cache = self.attenuation_distance
        if self.shape and not self.boundary:
            self.build_boundary()
            # only run this once the object exists in the db, since we depend on
            # the db to do this calculation
            if self.id and not self.attenuation_border:
                self.build_attenuation_buffer_line()

    project = models.ForeignKey(Project)
    activeyn = models.BooleanField(default=False)
    code = models.CharField(max_length=10)
    maxvolume = models.FloatField()
    minvolume = models.FloatField()
    uri = models.URLField()
    backupuri = models.URLField(blank=True)

    shape = models.MultiPolygonField(geography=True, null=True)
    boundary = models.GeometryField(geography=True, null=True, editable=False)

    attenuation_distance = models.IntegerField()
    attenuation_border = models.GeometryField(geography=True, null=True, editable=False)

    objects = models.GeoManager()

    def __unicode__(self):
        return str(self.id) + ": " + " : " + self.uri

    def save(self, *args, **kwargs):
        shape_changed = (self.shape != self._shape_cache)
        attenuation_distance_changed = self.attenuation_distance != self._attenuation_distance_cache
        # check if this is a new speaker or an updated speaker
        speaker_id = self.id
        # if we have modified the shape, update the border field
        if shape_changed:
            self.build_boundary()

        super(Speaker, self).save(*args, **kwargs)

        # after saving to the db, run the attenuation border builder if
        # this is a new speaker or if the shape or attenuation border have changed
        if (speaker_id == None) or (shape_changed or attenuation_distance_changed):
            self.build_attenuation_buffer_line()

    def build_boundary(self):
        self.boundary = self.shape.boundary

    def build_attenuation_buffer_line(self):
        from django.db import connection
        cursor = connection.cursor()
        raw_sql = """UPDATE {table} SET attenuation_border = ST_Boundary(ST_Buffer(shape, -attenuation_distance)::geometry)::geography where id = {speaker_id};
        """.format(table=self._meta.db_table, speaker_id=self.id)
        cursor.execute(raw_sql)

    def location_map(self):
        html = """<input type="text" value="" id="searchbox" style=" width:700px;height:30px; font-size:15px;">
        <div id="map_instructions">To change or select location, type an address above and select from the available options;
        then move pin to exact location of asset.</div>
        <div class="GMap" id="map" style="width:800px; height: 600px; margin-top: 10px;"></div>"""
        return html

    location_map.short_name = "location"
    location_map.allow_tags = True


class Tag(models.Model):
    """
    Metadata describing Assets
    """
    FILTERS = (
        ("", "No filter"),
        ("_within_10km", "Assets within 10km."),
        ("_ten_most_recent_days", "Assets created within 10 days."),
    )
    project = models.ForeignKey(Project, null=True, blank=False)
    tag_category = models.ForeignKey('TagCategory')
    value = models.TextField()
    description = models.TextField(null=True, blank=True)
    loc_description = models.ManyToManyField(
        LocalizedString, blank=True, related_name='tag_desc')
    loc_msg = models.ManyToManyField(LocalizedString, blank=True)
    data = models.TextField(null=True, blank=True)
    filter = models.CharField(
        max_length=255, default="", null=False, blank=True, choices=FILTERS)
    location = models.MultiPolygonField(geography=True, null=True, blank=True)

    # DEPRECATED: Used in API/1; could be generated from API/2 data
    relationships_old = models.ManyToManyField(
        'self', symmetrical=True, related_name='related_to', blank=True)

    def get_loc(self):
        return "<br />".join(unicode(t) for t in self.loc_msg.all())
    get_loc.short_description = "Localized Names"
    get_loc.name = "Localized Names"
    get_loc.allow_tags = True

    # relationships_old is used only in API/1
    def get_relationships_old(self):
        return [rel['pk'] for rel in self.relationships_old.all().values('pk')]

    def __unicode__(self):
        return self.tag_category.name + " : " + self.value

    class Meta:
        app_label = 'rw'  # necessary for special tag batch add form


class TagCategory(models.Model):
    """
    Tag groupings
    """
    name = models.CharField(max_length=50)
    data = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return str(self.id) + ":" + self.name

    class Meta:
        verbose_name = 'Tag Category'
        verbose_name_plural = 'Tag Categories'


class TagRelationship(models.Model):
    """
    Allows Tags to be tiered for more complex filtering and interactions
    """
    tag = models.ForeignKey(Tag)
    parent = models.ForeignKey("self", null=True, blank=True)

    def __unicode__(self):
        return str(self.id) + self.tag.value + str(self.parent)

    class Meta:
        verbose_name = 'Tag Relationship'
        verbose_name_plural = 'Tag Relationships'


class TimedAsset(models.Model):
    """
    Items to play at specific times of the stream duration.
    """
    project = models.ForeignKey(Project)
    asset = models.ForeignKey(Asset)
    # Asset start time in seconds
    start = models.FloatField()
    # Asset end time in seconds
    end = models.FloatField()

    def __unicode__(self):
        return "%s: Asset id: %s: Start: %s: End: %s" % (self.id, self.asset.id, self.start, self.end)

    class Meta:
        verbose_name = 'Timed Asset'
        verbose_name_plural = 'Timed Assets'


class UIGroup(models.Model):
    """
    A representation of how Tags should be grouped in client UI
    """
    SINGLE = 'single'
    MULTI = 'multi'
    MULTI_MIN_ONE = 'min_one'
    SELECT_METHODS = (
        (SINGLE, 'single'),
        (MULTI, 'multi'),
        (MULTI_MIN_ONE, 'multi_at_least_one'),
    )
    LISTEN = 'listen'
    SPEAK = 'speak'
    BROWSE = 'browse'
    UI_MODES = (
        (LISTEN, 'listen'),
        (SPEAK, 'speak'),
        (BROWSE, 'browse')
    )
    name = models.CharField(max_length=50)
    header_text_loc = models.ManyToManyField(
        LocalizedString, blank=True)
    ui_mode = models.CharField(default=LISTEN, max_length=6, blank=False,
                               choices=UI_MODES)
    tag_category = models.ForeignKey(TagCategory)
    select = models.CharField(default=SINGLE, max_length=7, blank=False,
                              choices=SELECT_METHODS)
    active = models.BooleanField(default=True)
    index = models.IntegerField()
    project = models.ForeignKey(Project)

    def get_header_text_loc(self):
        return "<br />".join(unicode(t) for t in self.header_text_loc.all())
    get_header_text_loc.short_description = "Localized Header Text"
    get_header_text_loc.name = "Localized Header Text"
    get_header_text_loc.allow_tags = True

    def toTagDictionary(self):
        return {'name': self.name,
                'code': self.tag_category.name,
                'select': self.get_select_display(),
                'order': self.index
                }

    def save(self, *args, **kwargs):
        super(UIGroup, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.id) + ":" + self.project.name + ":" + self.get_ui_mode_display() + ":" + self.name

    class Meta:
        verbose_name = 'UI Group'
        verbose_name_plural = 'UI Groups'
        ordering = ('index',)


class UIItem(models.Model):
    """
    A representation of how Tags should be displayed in client UI
    """
    ui_group = models.ForeignKey(UIGroup)
    index = models.IntegerField()
    tag = models.ForeignKey(Tag)
    default = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    parent = models.ForeignKey("self", null=True, blank=True)
    # def toTagDictionary(self):
    # return {'tag_id':self.tag.id,'order':self.index,'value':self.tag.value}

    def __unicode__(self):
        return str(self.id) + ":" + self.ui_group.name + ":" + self.tag.tag_category.name

    class Meta:
        verbose_name = 'UI Item'
        verbose_name_plural = 'UI Items'
        ordering = ('index',)


class UserProfile(models.Model):
    """
    Extends built-in Django User functionality
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    device_id = models.CharField(max_length=255, null=True)
    client_type = models.CharField(max_length=255, null=True)


class Vote(models.Model):
    """
    User-registered votes on specific Assets or other Users
    """
    LIKE = 'like'
    FLAG = 'flag'
    RATE = 'rate'
    BLOCK_ASSET = 'block_asset'
    BLOCK_USER = 'block_user'
    VOTE_TYPES = (
        (LIKE, 'like'),
        (FLAG, 'flag'),
        (RATE, 'rate'),
        (BLOCK_ASSET, 'block_asset'),
        (BLOCK_USER, 'block_user'),
    )
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    value = models.IntegerField(null=True, blank=True)
    session = models.ForeignKey(Session)
    asset = models.ForeignKey(Asset)
    type = models.CharField(max_length=16, choices=VOTE_TYPES)

    def __unicode__(self):
        return str(self.id) + ": Session id: " + str(self.session.id) + ": Asset id: " + str(self.asset.id) + ": Type: " + str(self.type)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=settings.AUTH_USER_MODEL)


def get_field_names_from_model(model):
    """Pass in a model class. Return list of strings of field names"""
    return [f.name for f in model._meta.fields]


def calculate_volume(speaker, listener):
    logger.debug("calculating volume of {} for {}".format(speaker, listener))
    try:
        listener_location = Point(listener['longitude'], listener['latitude'], srid=speaker.shape.srid)
        speaker_qset = Speaker.objects.filter(id=speaker.id)
        distance = speaker_qset.distance(listener_location, field_name='boundary').get().distance.m
        logger.debug("distance = %s", distance)
        if distance < speaker.attenuation_distance:
            # if the listener is within the attenuation buffer
            # scale the attenuation value to between the speaker's min and max volumes
            attenuation_percent = (speaker.attenuation_distance - distance) / speaker.attenuation_distance
            vol = (speaker.maxvolume - speaker.minvolume) * (1 - attenuation_percent) + speaker.minvolume
            logger.debug("attenuating speaker: {}%".format(attenuation_percent * 100))
        else:
            vol = speaker.maxvolume

        logger.debug("new volume: {} (min: {}, max: {})".format(vol, speaker.minvolume, speaker.maxvolume))
        return vol
    except Exception, e:
        logger.error(e)
        return 0
