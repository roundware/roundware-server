---
page_title: "Testing Roundware"
sidebar_current: "installation-testing"
---

# Testing your Roundware Installation

## Overview

After you have installed Roundware, you can run some API calls to test behaviour.  A default database is included in the base install so that you will have a fully-functional system with a test project in place immediately.  This test project will also serve as an example for the setup of future projects.

The following API calls will mimic a series of requests that will happen during a typical client session.  Port 8888 will access the python runserver instance and port 8080 the standard running instance.

### get_config

```
http://localhost:8888/api/1?operation=get_config&project_id=1
```

### get_tags

```
http://localhost:8888/api/1?operation=get_tags&project_id=1
```

### request_stream

```
http://localhost:8888/api/1?operation=request_stream&session_id=1&latitude=1&longitude=1
```

Expected response:

```
{
    "stream_url": "http://localhost:8000/stream1.mp3"
}
```

You can listen to the stream in a browser to make sure it is playing back properly.  You should hear ambient music and the test recording will play back as part of the stream immediately for between 10 and 30 seconds.

### modify_stream

First modify the stream with all available tags within range of the speaker:

```
http://localhost:8888/api/1?operation=modify_stream&session_id=1&tags=3,4,5,8,9,22
```

The test asset will play in the stream again, but if you modify the stream without one of the tags assigned to the test asset, the asset will not be played again:

```
http://localhost:8888/api/1?operation=modify_stream&session_id=1&tags=4,5,8,9,22
```

### move_listener

If you move the listener outside of the range of the speaker, the stream will fade out:

```
http://localhost:8888/api/1?operation=move_listener&session_id=1&latitude=5&longitude=5
```

And when you move the listener back within range, the speaker stream will fade back in and the test asset will play again:

```
http://localhost:8888/api/1?operation=move_listener&session_id=1&latitude=1&longitude=1
```

### create_envelope

In order to upload an asset from a client, you must first create a new envelope to add the asset to:

```
http://localhost:8888/api/1/?operation=create_envelope&session_id=1
```

Expected response:

```
{
    "envelope_id": 2
}
```

### add\_asset\_to\_envelope

With an envelope in hand, you can upload a file and add it to the envelope:

```
http://localhost:8888/api/1?operation=add_asset_to_envelope&envelope_id=2&latitude=1&longitude=1&tags=3,5,8&mediatype=audio
```
The audio file itself must be included in a POST part of this request.

We recommend using the [Postman app for Chrome](http://www.getpostman.com/) to do the web API testing as it provides a very convenient interface for creating, sending and otherwise managing API requests.  It also makes it easy to attach binaries in POST calls for uploading files.
