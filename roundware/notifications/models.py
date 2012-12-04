from django.contrib.auth.models import User
from django.core import urlresolvers
from django.core.mail import EmailMultiAlternatives
from django.db import models
from roundware.rw.models import Project

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

    def notify(self):
        if self.action in [0,1]:
            link = self.notification.get_absolute_url()
            self.message = "%s\n%s" % (self.message, link)

        email = EmailMultiAlternatives(
            subject='',
            body=self.message,
            from_email='info@roundware.com',
            to=[user.email for user in self.who.all() if user.has_perm('view_project', self.notification.project)],
        )
        email.send()