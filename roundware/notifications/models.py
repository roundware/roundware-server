from __future__ import unicode_literals
import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.db import models
from guardian.models import UserObjectPermission
from roundware.rw.models import Project
import logging

logger = logging.getLogger(__name__)

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
    project = models.ForeignKey(Project, on_delete = models.CASCADE)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return "%(model)s (%(project)s)" % {'model': ENABLED_MODELS[self.model][1], 'project': self.project}

    def get_absolute_url(self):
        return reverse("admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name), args=(self.id,))


class ActionNotification(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    action = models.IntegerField(choices=ENABLED_ACTIONS)
    who = models.ManyToManyField(User, related_name="notifications")
    message = models.TextField()
    subject = models.CharField(max_length=255, blank=True)
    notification = models.ForeignKey(ModelNotification, on_delete = models.CASCADE)
    # TODO: The default for last_sent_time is supposed to be:
    # datetime.datetime.now() - datetime.timedelta(hours=1)
    last_sent_time = models.DateTimeField(null=True)
    last_sent_reference = models.IntegerField(null=True)
    active = models.BooleanField(default=True)

    def is_active(self):
        """
        Returns Boolean.
        Returns True if both the ActionNotification and its parent ModelNotification are active
        """
        return bool(self.active and self.notification.active)

    def notify(self, ref=None):
        """
        Notify the associated users when the notification triggers
        """
        message = self.message
        # include a link to the admin page if the object is being added or
        # edited
        if self.action in [0, 1]:
            link = "http://%(domain)s%(abs)s" % {'domain': Site.objects.get_current().domain,
                                                 'abs': reverse("admin:%s_%s_change" % ("rw", ENABLED_MODELS[self.notification.model][1].lower()), args=(ref,))}
            message = "%s\n%s" % (self.message, link)

        # create the email object
        email = EmailMultiAlternatives(
            subject=self.subject,
            body=message,
            from_email=getattr(settings, "EMAIL_HOST_USER", "info@localhost"),
            # only send to users who have permissions through django-guardian to access the associated project
            # TODO: this only works when the ModelNotification points to a
            # 'Asset' will need to be adjusted when additional models are to be
            # added.
            to=[user.email for user in self.who.all() if UserObjectPermission.objects.filter(user=user,
                                                                                             permission__codename="access_project",
                                                                                             object_pk=self.notification.project.pk) or user.is_staff],
        )
        self.last_sent_time = datetime.datetime.now()
        self.last_sent_reference = ref
        self.save()
        try:
            ret = email.send()
            logger.info("Email Sent: %(email)s, %(ret)s" %
                    {'email': email.to, 'ret': ret})
        except:
            logger.info("Email send failed; check email account settings.")
