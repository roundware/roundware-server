---
page_title: "Admin - Notifications"
sidebar_current: "admin-notifications"
---

# Notifications Admin

<div class="alert alert-block alert-info">
    <p>
        <strong>DEFINITION:</strong> Emails messages sent to specified addresses triggered by activity on a particular model.  The most common
        notification is triggered when a new asset is created.
    </p>
</div>

Notifications are a separate custom Django App and are therefore accessed from the top level of the Django admin:

![Home Notifications](../docimg/admin/home-notifications.png)

Click `Model Notifications` to open the app admin.  Then click `Add model notification` to create a new notification:

![Notification Detail](../docimg/admin/notification-detail.png)

Currently, the only model for which notifications can be created  is the `asset` model.  The system is extensible,
so additional models can be added in the future as the need presents itself.

NEXT: [users and groups](authentication.html)