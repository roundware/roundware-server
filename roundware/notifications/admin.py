from __future__ import unicode_literals
from django.contrib import admin
from roundware.notifications.models import ModelNotification, ActionNotification


class ActionNotificationInline(admin.TabularInline):
    model = ActionNotification
    filter_horizontal = ['who']
    fieldsets = (
        ("Notification Options", {'fields': ('active', 'action')}),
        ("Email Options", {'fields': ('who', 'subject', 'message')})
    )


class ModelNotificationAdmin(admin.ModelAdmin):
    inlines = [ActionNotificationInline]
    list_filter = ('active', 'project')
    list_display = ('__unicode__', 'active',)
    list_editable = ('active',)

admin.site.register(ModelNotification, admin_class=ModelNotificationAdmin)
