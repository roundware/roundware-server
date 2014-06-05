---
page_title: "skip_ahead"
sidebar_current: "api-skip-ahead"
---

# skip_ahead

Allows client to tell server to fade out current recording and immediately begin playing the next recording per current filters.
This is useful if you want to offer users the ability to skip past something they are not interested in listening
to.

**Example Call:**

```
http://rw.roundware.org/roundware/?operation=skip_ahead&session_id=1
```

## Parameters (some optional*):

* `session_id`

### session_id

Indicates which stream the operation should be performed on.


## Response

JSON response is success boolean, indicating that the operation was received by the server.

### Example Response

```
{"success": true}
```
