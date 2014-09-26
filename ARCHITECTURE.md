# Roundware File Structure Architecture

This document describes the Roundware system file structure.

`roundware` - A Django project hosting the web admin, APIv1(currently) and API2.

`roundware/settings` - The Roundware configuration settings for dev, test, and
live environments.

`roundware/rw` - The Django web admin and Roundware database models.

`roundware/lib` - Common functionality used by rw/api1/api2 to process audio and
communicate with rwstreamd.py instances via dbus.

`roundware/api1` - The original Roundware API, it is partially REST based.

`roundware/api2` - The Roundware fully RESTful API V2.

`roundware/notifications` - The email notifications system. Can be used to notify
Roundware administrators when new database objects have been created or
updated.

`roundwared` - rwstreamd.py is the audio stream control daemon. It communicates
with the rest of the Roundware system via dbus, generates MP3/OGG audio streams
using gstreamer and creates audio streams using icecast2.
