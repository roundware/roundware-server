---
page_title: "log_event"
sidebar_current: "api-log-event"
---

# log_event

Used to indicate to the server when the user has performed and action that we want to log in the database, including start_record, stop_record, start_stream, stop_stream, start_upload, stop_upload.  Roundware uses this mechanism to log all client/server interactions - *anonymously* - in order to analyze usage patterns and better understand how participants are experiencing the system.

All parameter data is simply passed through to the corresponding fields in the `event` object.

In addition to `log_event` calls, events can be logged directly by the server as a result of another action.

**Example Call:**

```
http://rw.roundware.org/roundware/?operation=log_event&session_id=1&event_type=modify_stream&latitude=1&longitude=1&tags=1,2,3
```

## Parameters (some optional*):

* `session_id`
* `event_type`
* `latitude`*
* `longitude`*
* `client_time`
* `tags`*
* `data`*

### session_id

Events are grouped by `session_id` in order to report and analyze data on a session-by-session basis.

### event_type

Records what type of action/event has occurred. This is an unrestricted field, but the pirmary ones are:
`start_record`, `stop_record`, `start_stream`, `stop_stream`, `start_upload`, `stop_upload`, `client_error`,
`cleanup_session`, `heartbeat`, `modify_stream`, `start_session`.

### latitude

*OPTIONAL:* helpful in particular for plotting Session Maps

### longitude

*OPTIONAL:* helpful in particular for plotting Session Maps

### client_time

*OPTIONAL:* Useful to track differnces between client time and server time as indicated with timestamp

### tags

*OPTIONAL:* helpful in tandem with modify_stream event_types for logging which tags users are most interested in hearing

### data

*OPTIONAL:* Used to store any extranneous data provided by the client or server pertaining to a particular
event.  The most common use is to contain an error message for events of `event_type=client_error`.

## Response

JSON response is success boolean, indicating that the event was properly logged in the database

### Example Response

```
{"success": true}
```
