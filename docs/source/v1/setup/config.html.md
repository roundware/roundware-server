---
page_title: "Config"
sidebar_current: "setup-config"
---


# Roundware Config

Roundware has a default config file as well as the option of having project-specific config files.  All Roundware config files are stored by default in `/etc/roundware/` and the default config is at `/etc/roundware/rw`

```
# network interface used
interface = eth0
# default port for icecast streams
icecast_port = 8000
# default location for participant audio (see asset table in db)
audio_dir = /var/www/rwmedia
# default location for incoming participant audio - may be used if incoming audio is ingested before included in piece
upload_dir = /var/www/rwmedia
# log file location
log_file = /var/log/roundware
# process id file
pid_file = /var/run/roundware.pid
# database auth
dbuser = round
dbpasswd = round
dbname = roundware
# settings
num_pan_steps = 200         # discrete steps
stereo_pan_interval = 10      # milliseconds
ping_interval = 10000       # milliseconds
master_volume = 3.0
# determines connectivity to client.  When client stops beating, session is ended.  Time out in seconds.
active_stream_check_scheme = heartbeat
heartbeat_timeout = 200
# recording radius in meters
recording_radius = 10
external_host_name_without_port = http://roundware.org
```

You need to edit the default config file to change `external_host_name_without_port` to the url of your RW server or else RW will return stream urls with the incorrect server.

You should also go over the other parameters in the config just to make sure they correspond to your setup, such as the database info.