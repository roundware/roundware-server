import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.core.mail import EmailMultiAlternatives
from django.db import models
from roundware.rw.models import Project
import logging

logger = logging.getLogger("notifications")

ENABLED_MODELS = (
    (0, "Asset"),
#    (1, "Project"),
)

ENABLED_ACTIONS = (
    (0, "add"),
    (1, "edit"),
    (2, "delete"),
)

class ModelNotification(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    model = models.IntegerField(choices=ENABLED_MODELS)
    project = models.ForeignKey(Project)

    def __unicode__(self):
        return "%(model)s (%(project)s)" % {'model' : ENABLED_MODELS[self.model][1], 'project' : self.project}

    def get_absolute_url(self):
        return urlresolvers.reverse("admin:%s_%s_change" % (self._meta.app_label, self._meta.module_name), args=(self.id,))

class ActionNotification(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    action = models.IntegerField(choices=ENABLED_ACTIONS)
    who = models.ManyToManyField(User, related_name="notifications")
    message = models.TextField()
    subject = models.CharField(max_length=255, blank=True)
    notification = models.ForeignKey(ModelNotification)
    last_sent_time = models.DateTimeField(null=True)
    last_sent_reference = models.IntegerField(null=True, default=datetime.datetime.now() - datetime.timedelta(hours=1))

    def notify(self, ref=None):
        message = self.message
        if self.action in [0,1]:
            link = "http://%(domain)s%(abs)s" % {'domain' : Site.objects.get_current().domain,
                                                 'abs' : urlresolvers.reverse("admin:%s_%s_change" % ("rw", ENABLED_MODELS[self.notification.model][1].lower()), args=(ref,))}
            message = "%s\n%s" % (self.message, link)

        email = EmailMultiAlternatives(
            subject=self.subject,
            body=message,
            from_email=getattr(settings, "EMAIL_HOST_USER", "info@localhost"),
            to=[user.email for user in self.who.all() if user.has_perm('view_project', self.notification.project)],
        )
        self.last_sent_time = datetime.datetime.now()
        self.last_sent_reference=ref
        self.save()
        ret = email.send()
        logger.info("Email Sent: %(email)s, %(ret)s" % {'email' : email.to, 'ret' : ret})
