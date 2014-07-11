from __future__ import unicode_literals
import logging
import datetime
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from roundware.notifications.models import ActionNotification, ENABLED_MODELS

__author__ = 'jule'
logger = logging.getLogger(__name__)


def send_notifications_add_edit(sender, instance, created, *args, **kwargs):
    # get the type of model from the sender
    object_string = sender._meta.object_name.lower()
    logger.debug("Add or Edit %s, created: %s" %
                (object_string, created))
    # check whether the model is represented as being able to handle
    # notifications
    objects = [i[0] for i in ENABLED_MODELS if i[1].lower() == object_string]
    if objects:
        # 0 = add
        # 1 = edit
        action = 0 if created else 1
        logger.debug("%s %s", object_string, instance.id)
        object_int = objects[0]
        # find the time between this notifications and the last time this
        # notification was sent
        date_diff = datetime.datetime.now() - \
            datetime.timedelta(
                seconds=getattr(settings, "NOTIFICATIONS_TIME_BETWEEN", 30))
        # get the enabled notifications
        notifications = ActionNotification.objects.filter(
            notification__model=object_int,
            notification__project=instance.project,
            notification__active=True,
            action=action,
            active=True,
        )
        logger.debug("Enabled notifications: %s", notifications)
        # loop through and execute them
        for n in notifications:
            # only execute notification if we're working with a different object
            # or enough time has past since the last notification
            if n.last_sent_reference != instance.id or (n.last_sent_reference == instance.id and n.last_sent_time < date_diff):
                # if an edit is caught, make sure that the object wasn't created within 2 seconds
                # this is to stop the app from sending two notifications when the save() method is called
                # during the object creation process.
                if action == 1 and ActionNotification.objects.filter(
                        notification__model=object_int,
                        last_sent_reference=instance.pk,
                        last_sent_time__gte=datetime.datetime.now(
                        ) - datetime.timedelta(seconds=2),
                        action=0):
                    return
                n.notify(ref=instance.id)


def send_notifications_delete(sender, instance, *args, **kwargs):
    object_string = sender._meta.object_name.lower()
    logger.info("caught delete %s", object_string)
    objects = [i[0] for i in ENABLED_MODELS if i[1].lower() == object_string]
    if objects:
        logger.info("%s %s", object_string, instance.id)
        object_int = objects[0]
        notifications = ActionNotification.objects.filter(
            notification__model=object_int,
            notification__project=instance.project,
            notification__active=True,
            action=2,
            active=True,
        )
        logger.info("%s", notifications)
        for n in notifications:
            n.notify(ref=instance.pk)

post_save.connect(send_notifications_add_edit)
post_delete.connect(send_notifications_delete)
