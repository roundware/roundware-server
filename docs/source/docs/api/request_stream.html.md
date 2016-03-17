---
page_title: "request_stream"
sidebar_current: "api-request-stream"
---

# request_stream

Generates an audio stream unique to the client based on parameters sent in request
and project audio settings (speakers and audiotracks).

**Example Call:**

```
http://localhost:8888/api/1/?operation=request_stream&session_id=1&latitude=1&longitude=1&tags=1,2,3
```

## Parameters (some optional*):

* `session_id`
* `latitude`*
* `longitude`*
* `tags`*
* `audio_stream_bitrate`*

### session_id

Each stream is unique to a session, so `session_id` is used to set a stream identifier for future
stream modification via `modify_stream`.

### latitude

*OPTIONAL:* initial latitude server uses to create stream mix.  Typically this is soon modified
by a `modify_stream` API call

### longitude

*OPTIONAL:* initial longitude server uses to create stream mix.  Typically this is soon modified
by a `modify_stream` API call

### tags

*OPTIONAL:* initial tags used to filter available assets.  If non provided, ALL tags for project are
assumed to be available.

### audio\_stream\_bitrate

*OPTIONAL:* Valid options are: 64, 96, 112, 128, 160, 192, 256 and 320.  If parameter is passed, the stream will be generated with this bitrate.  If no parameter is passed stream will be generated with a bitrate determined by `rw_project.audio_stream_bitrate`

## Response

JSON response is a stream mountpoint that can be used by any client audio streamer to play the audio.

### Example Response

```
{
    "stream_url": "http://rw.roundware.org:8000/stream1.mp3"
}
```
