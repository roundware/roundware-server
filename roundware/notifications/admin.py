from django.contrib import admin
from roundware.notifications.models import ModelNotification, ActionNotification

class ActionNotificationInline(admin.TabularInline):
    model = ActionNotification
    filter_horizontal = ['who']

class ModelNotificationAdmin(admin.ModelAdmin):
    inlines = [ActionNotificationInline]

admin.site.register(ModelNotification, admin_class=ModelNotificationAdmin)