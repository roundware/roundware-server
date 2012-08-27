from django.db import models
from roundware.settings import AUDIO_FILE_URI

import datetime

class BigIntegerField(models.IntegerField):
    empty_strings_allowed=False
    def get_internal_type(self):
        return "BigIntegerField"
    def db_type(self):
        return 'bigint' # Note this won't work with Oracle.

class Language(models.Model):
    language_code = models.CharField(max_length = 10)
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
    listen_questions_dynamic =  models.BooleanField()
    speak_questions_dynamic = models.BooleanField()
    sharing_message = models.TextField(null=True, blank=True)
    out_of_range_message = models.TextField(null=True, blank=True)
    sharing_message_loc = models.ManyToManyField(LocalizedString, related_name='sharing_msg_string', null=True, blank=True)
    out_of_range_message_loc = models.ManyToManyField(LocalizedString, related_name='out_of_range_msg_string', null=True, blank=True)
    out_of_range_url = models.CharField(max_length=512)
    recording_radius = models.IntegerField(null=True)
    listen_enabled = models.BooleanField()
    geo_listen_enabled = models.BooleanField()
    speak_enabled = models.BooleanField()
    geo_speak_enabled  = models.BooleanField()
    reset_tag_defaults_on_startup = models.BooleanField()
    legal_agreement = models.TextField(null=True, blank=True)
    legal_agreement_loc = models.ManyToManyField(LocalizedString, related_name='legal_agreement_string', null=True, blank=True)
    new_recording_email_body = models.TextField(null=True)
    new_recording_email_recipient = models.TextField(null=True)

    repeat_mode = models.ForeignKey(RepeatMode, null=True)
    def __unicode__(self):
            return self.name

    class Meta:
        permissions = (('access_project', 'Access Project'),)

class Session(models.Model):
    device_id = models.CharField(max_length=36, null=True, blank=True)
    starttime = models.DateTimeField()
    stoptime = models.DateTimeField(null=True, blank=True)
    project = models.ForeignKey(Project)
    ordering = ['id']
    language = models.ForeignKey(Language, null=True)
#    client_type = models.TextField(null=True, blank=True)
#    client_system = models.TextField(null=True, blank=True)
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

    def __unicode__(self):
            return self.tag_category.name + " : " + self.description

class MasterUI(models.Model):
    name = models.CharField(max_length=50)
    ui_mode = models.ForeignKey(UIMode)
    tag_category = models.ForeignKey(TagCategory)
    select = models.ForeignKey(SelectionMethod)
    active = models.BooleanField(default=True)
    index = models.IntegerField()
    project = models.ForeignKey(Project)
    def toTagDictionary(self):
        return {'name':self.name,'code':self.tag_category.name,'select':self.select.name,'order':self.index}
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
    def __unicode__(self):
            return "Track " + str(self.id)

class EventType(models.Model):
    name = models.CharField(max_length=50)
    ordering = ['id']

class Event(models.Model):
    server_time = models.DateTimeField()
    client_time = models.CharField(max_length=50,null=True, blank=True)
    session = models.ForeignKey(Session)

    event_type = models.CharField(max_length=50)
    data = models.TextField(null=True, blank=True)
    latitude = models.CharField(max_length=50,null=True, blank=True)
    longitude = models.CharField(max_length=50,null=True, blank=True)
    tags = models.TextField(null=True, blank=True)

    operationid = models.IntegerField(null=True, blank=True)
    udid = models.CharField(max_length=50,null=True, blank=True)

class Asset(models.Model):
    session = models.ForeignKey(Session,null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    filename = models.CharField(max_length=256,null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)

    submitted = models.BooleanField(default=True)
    project = models.ForeignKey(Project, null=True, blank=True)

    created = models.DateTimeField(default=datetime.datetime.now)
    audiolength = models.BigIntegerField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, null=True, blank=True)
    language = models.ForeignKey(Language, null=True)

    tags.tag_category_filter = True

    audiolength.audio_length_filter = True

    def audio_player(self):
        return """<div data-filename="%s" class="audio-file"></div>""" % self.filename
    audio_player.short_name = "audio"
    audio_player.allow_tags = True

    def norm_audiolength(self):
        if self.audiolength:
            return "%.2f s" % (self.audiolength / 1000000000.0,)
    norm_audiolength.short_description = "Audio Length"
    norm_audiolength.name = "Audio Length"
    norm_audiolength.allow_tags = True

    def audio_link_url(self):
        return '<a href="%s/%s" target="_new">%s</a>' % (AUDIO_FILE_URI, self.filename, self.filename)
    audio_link_url.allow_tags = True

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
            print v
            dict_num = votes_dict.get(v.type, 0)
            if v.value is None:
                value = 0
            else:
                value = v.value
            t_dict = {v.type : dict_num + value }
            votes_dict.update(t_dict)
        if dict:
            return votes_dict
        return ", ".join("%s : %d" % (v, num) for v, num in votes_dict.items())

    get_votes.short_description = "Votes"
    get_votes.name = "Votes"

    def __unicode__(self):
        return str(self.id) + ": " + str(self.latitude) + "/" + str(self.longitude)

class Envelope(models.Model):
    session = models.ForeignKey(Session)
    assets = models.ManyToManyField(Asset)
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

class ListeningHistoryItem(models.Model):
    session = models.ForeignKey(Session)
    asset = models.ForeignKey(Asset)
    starttime = models.DateTimeField()
    duration = models.BigIntegerField(null=True, blank=True)
    def __unicode__(self):
            return str(self.id) + ": Session id: " + str(self.session.id) + ": Asset id: " + str(self.asset.id) + " duration: " + str(self.duration)

class Vote(models.Model):
    value = models.IntegerField(null=True, blank=True)
    session = models.ForeignKey(Session)
    asset = models.ForeignKey(Asset)
    type = models.CharField(max_length=16)
    def __unicode__(self):
            return str(self.id) + ": Session id: " + str(self.session.id) + ": Asset id: " + str(self.asset.id) + ": Value: " + str(self.value)
