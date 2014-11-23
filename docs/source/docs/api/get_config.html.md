---
page_title: "get_config"
sidebar_current: "api-get-config"
---

# get_config

**Example Call:**

```
http://localhost:8888/api/1/?operation=get_config&project_id=1
```

This is typically the first command a Roundware client sends to the Roundware server.
It establishes a new session and supplies configuration data to the client.

## Parameters (some optional*):

* `project_id`
* `device_id`*
* `client_type`*
* `client_system`*
* `language`*

## project_id

id from the database for the project that the client wishes to interact with and
for which it is built.

## device_id

*OPTIONAL:* Roundware assigns a device_id to each client device in order to track repeat usage.
If the client is using Roundware for the first time, no `device_id` is sent and one is
generated and returned by the server and stored by the client.  Once a device has a
`device_id`, it sends it to the server as a parameter of `get_config`.

Stored in `rw_session.device_id`

## client_type

*OPTIONAL:* Examples are iPhone, iPad, Samsung Galaxy S4 etc

Stored in `rw_session.client_type`

## client_system

*OPTIONAL:* For example, Android 4.1.2, iPhone OS-7.0.4 etc

Stored in `rw_session.client_system`

## language

*OPTIONAL:* For localization purposes, each session is assigned a language.  This is
sent from the client to the server in the ISO 2-character language code (i.e. 'en', 'fr', 'es' etc).

If no language is sent, default language of 'en' is assumed.

Stored in `rw_session.language_id`

## Response

JSON response is broken into sections for device, session, project, server, speakers and audiotracks.
Device and session info is generated in real-time by the server; project, speaker and audiotrack info is
pulled directly from the database.

### Example Response

```
{
        "device": {
            "device_id": "12bf86e6-d84a-4d19-a65a-27860210287f"
        }
    },
    {
        "session": {
            "session_id": 11116
        }
    },
    {
        "project": {
            "audio_format": "mp3",
            "audio_stream_bitrate": "128",
            "demo_stream_enabled": true,
            "demo_stream_message": "This is a test demo stream message!",
            "demo_stream_url": "http://roundware.org:8000/rw_outofrange.mp3",
            "files_url": "http://roundware.org/rw.zip",
            "files_version": "2",
            "geo_listen_enabled": false,
            "geo_speak_enabled": true,
            "legal_agreement": "By clicking below, you agree that any recording you make using this app can be used for any purpose. Thanks and enjoy!",
            "listen_enabled": true,
            "listen_questions_dynamic": false,
            "max_recording_length": 30,
            "out_of_range_message": "Test out of range message",
            "project_id": 1,
            "project_name": "Test Project",
            "recording_radius": 20,
            "reset_tag_defaults_on_startup": true,
            "sharing_message": "Listen to this recording I made with a #roundware project!",
            "sharing_url": "http://roundware.org/r/eid=[id]",
            "speak_enabled": true,
            "speak_questions_dynamic": false
        }
    },
    {
        "server": {
            "version": "2.0"
        }
    },
    {
        "speakers": [
            {
                "activeyn": false,
                "backupuri": "http://roundware.org:8000/rw.mp3",
                "code": "RW",
                "id": 3,
                "latitude": 47.67298126,
                "longitude": -122.36761475,
                "maxdistance": 1000,
                "maxvolume": 1.0,
                "mindistance": 100,
                "minvolume": 0.0,
                "project_id": 1,
                "uri": "http://roundware.org:8000/rw.mp3"
            },
            {
                "activeyn": true,
                "backupuri": "http://roundware.org:8000/rw2.mp3",
                "code": "RW2",
                "id": 6,
                "latitude": 38.8902,
                "longitude": -77.036299999999997,
                "maxdistance": 10000,
                "maxvolume": 0.59999999999999998,
                "mindistance": 1000,
                "minvolume": 0.0,
                "project_id": 1,
                "uri": "http://roundware.org:8000/rw2.mp3"
            }
        ]
    },
    {
        "audiotracks": [
            {
                "id": 1,
                "maxdeadair": 3000000000.0,
                "maxduration": 180000000000.0,
                "maxfadeintime": 500000000.0,
                "maxfadeouttime": 2000000000.0,
                "maxpanduration": 10000000000.0,
                "maxpanpos": 0.0,
                "maxvolume": 1.0,
                "mindeadair": 1000000000.0,
                "minduration": 180000000000.0,
                "minfadeintime": 100000000.0,
                "minfadeouttime": 100000000.0,
                "minpanduration": 5000000000.0,
                "minpanpos": 0.0,
                "minvolume": 1.0,
                "project_id": 1,
                "repeatrecordings": false
            }
        ]
    }
]
```

<!-- <div class="alert alert-block alert-warn">
<strong>Checksums for versioned boxes or boxes from Vagrant Cloud:</strong>
For boxes from Vagrant Cloud, the checksums are embedded in the metadata
of the box. The metadata itself is served over TLS and its format is validated.
</div> -->
