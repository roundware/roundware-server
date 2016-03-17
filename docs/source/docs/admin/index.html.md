---
page_title: "Admin"
sidebar_current: "admin"
---

# Roundware Admin

Roundware uses the Django Admin with some customizations as the core method for the setup and administration of Roundware projects.  We use
the [django-admin-bootstrapped](https://github.com/django-admin-bootstrapped/django-admin-bootstrapped) app to update the feel and flexibility of the admin.

The base Roundware install comes with a test project setup and ready to test the installation and with which to experiment.

This section will explain the basic Admin features and how to create and manage a customized Roundware project to suit your needs.
The Admin home screen displays all the available models, but this guide will focus on the primary ones.

## Admin Home Screen

![Admin Home](../docimg/admin/home.png)

Refer to the [Setup](../setup/index.html) documentation for more info on the individual fields in each model.

## General Admin Tips

Items in **BOLD** are required fields.

### Navigation

The Admin employs a basic breadcrumb-type navigation system at the top of each screen.  Each section is a link that
takes you back to the specified previous location within the Admin.

![Basic Navigation](../docimg/admin/navigation.png)

### List Filters

Many of the Admin list views have filtering capabilities, accessible via a dropdown in the upper right of the view.

![List Filters](../docimg/admin/list-filter.png)

### Localized Strings

Localized strings can be added directly from other model admin screens.  Look for the green plus:

![Localized String List](../docimg/admin/localized-string-list.png)

Clicking the green plus opens another window where a new localized string can be created and assigned to one of the available languages
in the installation.

![Localized String Detail](../docimg/admin/localized-string-detail.png)

Please use the sidebar links to explore the different Admin screens, starting with [`project`](project.html)

