import logging
import datetime
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from roundware.notifications.models import ActionNotification, ENABLED_MODELS

__author__ = 'jule'
logger = logging.getLogger("notifications")

def send_notifications_add(sender, instance, created, **kwargs):
    if not created:
        return
    logger.info("caught add")
    object_string = sender._meta.object_name.lower()
    logger.info("%s %s", object_string, instance.id)
    objects = [i[0] for i in ENABLED_MODELS if i[1].lower() == object_string]
    if objects:
        object_int = objects[0]
        date_diff = datetime.datetime.now() - datetime.timedelta(seconds=getattr(settings, "NOTIFICATIONS_TIME_BETWEEN", 30))
        notifications = ActionNotification.objects.filter(notification__model = object_int,
                                                          action = 0,
                                                          last_sent_time__lt=date_diff
                                                          )
        logger.info("%s", notifications)
        for n in notifications:
            n.notify(ref=instance.pk)

def send_notifications_edit(sender, instance, created, **kwargs):
    if created:
        return
    logger.info("caught edit")
    object_string = sender._meta.object_name.lower()
    logger.info("%s %s", object_string, instance.id)
    objects = [i[0] for i in ENABLED_MODELS if i[1].lower() == object_string]
    if objects:
        object_int = objects[0]
        date_diff = datetime.datetime.now() - datetime.timedelta(seconds=getattr(settings, "NOTIFICATIONS_TIME_BETWEEN", 30))
        notifications = ActionNotification.objects.filter(notification__model = object_int,
                                                          action = 1,
                                                          last_sent_time__lt=date_diff
                                                         )
        logger.info("%s", notifications)
        for n in notifications:
            n.notify(ref=instance.pk)

def send_notifications_delete(sender, instance, **kwargs):
    logger.info("caught delete")
    object_string = sender._meta.object_name.lower()
    logger.info("%s %s", object_string, instance.id)
    objects = [i[0] for i in ENABLED_MODELS if i[1].lower() == object_string]
    if objects:
        object_int = objects[0]
        notifications = ActionNotification.objects.filter(notification__model = object_int,
                                                          action = 2)
        logger.info("%s", notifications)
        for n in notifications:
            n.notify(ref=instance.pk)

post_save.connect(send_notifications_add)
post_delete.connect(send_notifications_delete)
post_save.connect(send_notifications_edit)