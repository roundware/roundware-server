---
page_title: "create_envelope"
sidebar_current: "api-create-envelope"
---

# create_envelope

Creates an entry in the envelope table in the db for an asset that is going to be uploaded later. Used primarily for the sharing functionality so that participants can share assets before the file is fully uploaded.

**Example Call:**

```
http://rw.roundware.org/roundware/?operation=create_envelope&session_id=1
```

## Parameters:

* `session_id`

### session_id

Envelopes are tied to their `session_id` for reporting and analysis purposes.


## Response

JSON response is the newly created `envelope_id`

### Example Response

```
{"envelope_id": 2}
```
