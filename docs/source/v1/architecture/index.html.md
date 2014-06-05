---
page_title: "Architecture"
sidebar_current: "architecture"
---

# Roundware Architecture

## Overview

Roundware provides a set of web service APIs to support location-based listening and visitor submission of media assets.  The architecture, outlined in the diagram below, depicts the different elements in a Roundware deployment.

* Apache Server: fields all incoming web requests and passes them to a running Roundware server via FCGI.
* Roundware:
 * `roundware` python module: built on Django, the roundware python module fields all incoming requests and provides data administration functionality.
 * `roundwared` python module: the ‘low-level’ roundware protocol implementation, the roundwared module provides the nuts and bolts of stream creation, dbus interaction and database interaction.
* dbus: a message bus system which is a standard part of the linux kernel.
* mysql: data store, exposed through the roundware python module via Django.
* icecast: open-source audio streaming software used by most internet radio stations among other things

## Diagram

![Roundware Architecture](http://roundware.org/images/rw_architecture.png)

## Message Flow

To illustrate interaction with the pieces mentioned above, we’ll narrate through a request stream and modify stream call, updating the location of the listener.

1. An incoming request stream call is marshaled from roundware to roundwared.  Roundwared looks up some session-specific data, then forks a process and starts the streamscript.
2. Streamscript constantly streams audio to icecast, which provides an outgoing stream to an individual listener. At the same time, streamscript receives incoming messages from roundware/roundwared over dbus to update location and listener preferences, which are reflected dynamically in the outgoing stream.
3. An incoming modify stream call is marshaled from roundware to roundwared, which here includes new location information (lat, lon) for a listener.  The streamscript instance for this particular listener (identified by session_id) is sent the updated location info via a dbus message, at which point the content streamed to icecast is modified according to the updated location.

## Further Explanation

The Roundware architecture is essentially this: a web service is called, forks a process which generates audio; this audio is sent to an icecast server; the process reads continuously from the database, the file system for audio, and makes calls to the icecast admin page while sending its audio stream. It also checks dbus messages for updates of various filters (tags and location) which are incoming from the web service.

**Stream Object:**

Let's start from the RoundStream class, located in `stream.py`. The stream class accepts a session\_id, a media format, and a request on startup.

The session\_id is the ID that has been created to identify the stream. The stream has to know which stream it is for several reasons. One is that it should report which stream it is when making important log entries, like when it is closing down. Two is that it's used when the stream creates an icecast client connection to stream its output to. It bases the URL it creates on the session\_id. Finally every stream needs a session\_id so that we may find the proper stream to send updates to when they are updated.

**Creation:**

The stream is created by instantiating the object. Walking backwards from there it's the streamscript that instantiates a stream and then becomes a background process. You can run this script with the arguments on the command line just to make a stream. This is a great debugging tool, especially when used in foreground mode. Walking backward from there, the streamscript, in actual production code, is run from a web service which accepts the arguments via POST or GET.

So, basically, you call a web service with a bunch of arguments, they are turned into command line arguments, and passed to a script that is forked off. The web service terminates, sending back the session\_id and URL of the stream and the forked process plays the audio to icecast.

With that data, the stream is created. The stream pulls from two major sources on creation. It pulls audiotracks from the database and also speakers. Audiotracks are where the recordings are played and speakers are where the background audio is played. All the speakers and compositions are pulled together and mixed (in the audio sense) in an adder (a gstreamer object) then it's sent to a sink specialized for Roundware that encodes it to the right format and sends it to the icecast server.

**Cleanup:**

A stream sets up a periodic check to see if anyone is listening and also checks the last time there was any stimulus sent to the stream. If it's been a long enough time without anyone listening or sending stimulus to the stream, the stream cleans itself up and closes down. The stimulus can be an update to the request, a change in location, or a heartbeat, which is a special kind of stimulus meant only to trigger an update to the last time a stimulus was seen so the stream doesn't die.

**Updates:**

Updates are done using dbus for interprocesses communication. Remember that the stream is a forked process, running independently on the server, and sending its audio to icecast. It checks itself for whether or not it should be cleaned up. So it's fully separated. It sets up a listener for a dbus socket and listens for messages pertaining to its session\_id as well. When the client calls a web service to update a stream, it passes the arguments and the session\_id. This gets turned into a dbus broadcast and the streams pick it up. If the session\_id matches for a stream, that stream acts on the update, and the other streams ignore the message. This dbus listener is setup by the streamscript right after the stream is instantiated.

This is the basic structure of the listening system. There's a lot of depth to how recordings are played, chosen, faded, panned, and a lot of nitty gritty about gstreamer low-level stuff. These things are fairly well encapsulated and able to be understood in isolation. The icecast admin is used for checking on the stream's activity/existence, the speakers mixer based on geolocation, the audiotracks playing the assets, which assets playing in the recording collection, the sink that sends the data to the icecast are all separate modules of classes that the stream relies on and you can dive deeper into whichever part you need to understand better.