---
page_title: "modify_stream"
sidebar_current: "api-modify-stream"
---

# modify_stream

Modifies an existing stream per new tag filters and/or location filters.

**Example Call:**

```
http://rw.roundware.org/roundware/?operation=modify_stream&session_id=1&latitude=1&longitude=1&tags=1,2,3
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
