---
page_title: "Settings"
sidebar_current: "setup-settings"
---


# Django Settings

Django is configured using a settings file which we store in `~/roundware-server/roundware/settings/common.py`.  It is highly recommended that you create a local settings file `~/roundware-server/roundware/settings/local_settings.py` in which to store settings specific to your environment, passwords, etc.

Here is a list of the most critical settings parameters that are specific to Roundware:

<table class="table table-striped table-bordered mr-types">
    <thead>
        <tr>
            <th>Parameter</th>
            <th>Format/Units</th>
            <th>Notes</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Master UI</td>
            <td>picklist</td>
            <td></td>
        </tr>
    </tbody>
</table>


Other settings found in the default settings file are primarily Django-specific and can be adjusted as needed, referring to the [Django documentation](http://djangoproject.org/docs).