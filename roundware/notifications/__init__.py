from django.db.models.signals import post_save, post_delete
from roundware.notifications.models import ActionNotification, ENABLED_MODELS

__author__ = 'jule'

def send_notifications_add(sender, instance, created, **kwargs):
    print "add"
    if not created:
        return
    object_string = sender._meta.object_name.lower()
    objects = [i[0] for i in ENABLED_MODELS if i[1].lower() == object_string]
    if objects:
        object_int = objects[0]
        notifications = ActionNotification.objects.filter(notification__model=object_int, action=0)
        for n in notifications:
            n.notify()

def send_notifications_edit(sender, instance, created, **kwargs):
    print "edit"
    if created:
        return

    object_string = sender._meta.object_name.lower()
    objects = [i[0] for i in ENABLED_MODELS if i[1].lower() == object_string]
    if objects:
        object_int = objects[0]
        notifications = ActionNotification.objects.filter(notification__model=object_int, action=1)
        for n in notifications:
            n.notify()

def send_notifications_delete(sender, instance, **kwargs):
    object_string = sender._meta.object_name.lower()
    objects = [i[0] for i in ENABLED_MODELS if i[1].lower() == object_string]
    if objects:
        object_int = objects[0]
        notifications = ActionNotification.objects.filter(notification__model=object_int, action=2)
        for n in notifications:
            n.notify()

post_save.connect(send_notifications_add)
post_delete.connect(send_notifications_delete)
post_save.connect(send_notifications_edit)