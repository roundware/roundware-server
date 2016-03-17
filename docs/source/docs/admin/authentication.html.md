---
page_title: "Admin - Authentication"
sidebar_current: "admin-authentication"
---

# Users and Groups

<!-- <div class="alert alert-block alert-info">
    <p>
        <strong>DEFINITION:</strong> The highest level of segmentation/grouping for all RW data.  One RW instance can run many projects simultaneously, governed by CPU, bandwidth and memory resources. Typically clients, mobile or web, are project-specific.
    </p>
</div> -->

Roundware uses Django's built-in authentication system.  You can create Users and Groups and assign different levels
of access to the models via the Admin.  Authentication is accessed from the Admin home screen:

![Authentication Home](../docimg/admin/home-notifications.png)

## Users

All Users in the system are listed:

![User List](../docimg/admin/user-list.png)

Editing User data and creating new Users is done from the User detail screen:

![User Detail](../docimg/admin/user-detail.png)

# Groups

Groups contain Users and define a set of privileges.  There are no default Groups setup in Roundware,
but depending on your circumstances, they can be advantageous.  To add a new Group, click **Add Group**,
name the new group and select the privileges for that Group.

![Group Detail](../docimg/admin/group-detail.png)

NEXT: [Object Permissions](permissions.html)