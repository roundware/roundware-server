---
page_title: "heartbeat"
sidebar_current: "api-heartbeat"
---

# heartbeat

Tells the server the client is still listening. The Roundware server will clean up streams that are not listened to
for a certain amount of time (set using the `heartbeat_timeout` parameter in the config file `/etc/roundware/rw`) in
order to efficiently use server resources.  In situations where a client wants to keep a stream alive for longer than
`heartbeat_timeout` without actually listening to the stream, the heartbeat API call can be sent at intervals shorter
than `heartbeat_timeout` to keep the stream alive indefinitely.  This is useful when a user is making a recording or
pauses the audio stream.

**Example Call:**

```
http://localhost:8888/api/1/?operation=heartbeat&session_id=1
```

## Parameters (some optional*):

* `session_id`

### session_id

`session_id` determines which stream to apply the heartbeat to.


## Response

JSON response is success boolean, indicating that the heartbeat was properly acknowledged by the server

### Example Response

```
{"success": true}
```
