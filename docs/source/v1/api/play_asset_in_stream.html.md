---
page_title: "play_asset_in_stream"
sidebar_current: "api-play-asset-in-stream"
---

# play\_asset\_in\_stream

Allows client to control what asset is played next in the stream.  Useful for replaying assets or
otherwise exerting more direct control over the content of the stream.

When this call is received the asset currently playing in the stream in question is faded out and
the new one is played thereafter.

**Example Call:**

```
http://localhost:8888/api/1/?operation=play_asset_in_stream&session_id=1&asset_id=32&delay=1000
```

## Parameters (some optional*):

* `session_id`
* `asset_id`
* `delay`*

### session_id

Indicates which stream the operation should be performed on.

### asset_id

Indicates which asset should be played next.

### delay

*OPTIONAL:* adds a delay time (in ms) between when the previous asset fades out and the newly
indicated asset begins playing. [this may not be functioning currently]


## Response

JSON response is success boolean, indicating that the operation was received by the server.

### Example Response

```
{"success": true}
```
