---
page_title: "modify_stream"
sidebar_current: "api-modify-stream"
---

# modify_stream

Modifies an existing stream per new tag filters and/or location filters.

If tag filters are included, Roundware will refresh the available recordings per the new tags.  If only latitude and longitude are included, available recordings will not be entirely refreshed so that recordings that have already been played will not get played again until the user leaves and re-enters the recording's range.

Roundware playback is based on tag categories.  Each asset in a project should be assigned one tag from each tag category in a typical situation.  If ```modify_stream``` is sent with any tags from a particular tag category, Roundware assumes that the category in question is active and there will not return assets that don't contain any tags from this category.

**Example Call:**

```
http://localhost:8888/api/1/?operation=modify_stream&session_id=1&latitude=1&longitude=1&tags=1,2,3
```

## Parameters (some optional*):

* `session_id`
* `latitude`*
* `longitude`*
* `tags`*

### session_id

`session_id` is used to determine which stream to modify.

### latitude

*OPTIONAL:* in combination with longitude, causes stream audio to be updated for the new location

### longitude

*OPTIONAL:* in combination with latitude, causes stream audio to be updated for the new location

### tags

*OPTIONAL:* causes available assets for stream to be filtered by new set of tags

## Response

JSON response is success boolean

### Example Response

```
{"success": true}
```
