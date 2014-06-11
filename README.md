# ROUNDWARE INSTALLATION GUIDE

## Overview

Roundware is a client-server system.  The server runs on Ubuntu Linux, version 12.04 LTS Precise Pangolin and clients are available for iOS, Android and HTML5 browsers.  This document outlines the steps required to setup a Roundware server with a basic installation that can be accessed through any of these clients.
For more information about Roundware functionalities and projects that use the platform, please check out:[roundware.org](http://roundware.org "Roundware")

## Requirements
In order to successfully install Roundware, the following requirements must be met:

 * server running Ubuntu 12.04 LTS Precise Pangolin
 * root access
 * familiarity with Apache, MYSQL, and icecast

Unless stated otherwise, all scripts referred to in this guide reside in the root directory of the Roundware distribution:

__roundware-server__

In order to successfully install all required packages, make sure `/etc/apt/sources.list` has multiverse repositories enabled.

## Pre-requisites 
Roundware requires many packages to support streaming and management.  Run the *INSTALL-prerequisites* script to install them:

	user@machine:~/roundware-server$ sh INSTALL-prereqs

All packages contained therein MUST be installed successfully to run Roundware fully.

## Icecast

Roundware uses Icecast to stream audio, much like internet radio stations.  After installation, Icecast requires some basic configuration to function properly with Roundware. In certain instances, icecast2 prompts during the install process for the hostname and passwords.  Hostname should be `localhost`.
Some configuration changes are required to the basic Icecast configuration, and they must be in sync with the configured values for Roundware.  These files must be edited as superuser (sudo). Sample icecast config files are included in the distribution in the `roundware-server/files` directory.
First, you'll edit the base icecast config.

	user@machine:$ sudo vim /etc/default/icecast2

Set/verify the enable value to true in the last line of this file:

	ENABLE=true

Next, you'll edit the base icecast config:

	user@machine:$ sudo vim /etc/icecast2/icecast.xml

Set passwords (in 3 places) to correspond with what is in the Roundware default configuration, currently set in `roundwared/settings.py`.  You may have already been prompted for these passwords during the icecast install process, in which case you should simply verify that they are in the xml.  The default config has the password 'roundice'.  Also, set the max number of sources to 100.

	<sources>100</sources>
	---
	<authentication>
        <!-- Sources log in with username 'source' -->
        <source-password>roundice</source-password>
        <!-- Relays log in username 'relay' -->
        <relay-password>roundice</relay-password>

        <!-- Admin logs in with the username given below -->
        <admin-user>admin</admin-user>
        <admin-password>roundice</admin-password>
	</authentication>

Restart Icecast for changes to take effect:

	user@machine:$ sudo /etc/init.d/icecast2 restart

To verify that icecast is up and running go to `http://<your.roundware.host>:8000` to see the default icecast admin page.

## MYSQL

Roundware uses MYSQL and requires a dedicated database with a dedicated user.  Create the default values for this user by running the `INSTALL-mysql` script.  You'll be prompted 3 times for your mysql root password, which you configured during installation.

	user@machine:~/roundware-server$ sh INSTALL-mysql

You may change the database name and account info to fit your needs, but if you do, be sure to change the Roundware config (`/etc/roundware/rw`) and the django settings (`roundware-server/roundware/settings.py`) to reflect your changes.

## Apache

Apache must be configured to forward requests to Roundware fastcgi endpoint.  A default config is included at `roundware-server/files/apache-config-example`.  If installing on a clean 12.04 machine, this file can simply be copied to the apache configuration directory, though there are several changes that should be made to reflect your environment.  Look for the following lines in the `apache-config-example`, and change them to reflect the location to which you've installed Roundware:

	DocumentRoot /home/ubuntu/roundware-server/roundware/
	FastCGIExternalServer /home/ubuntu/roundware-server/roundware/mysite.fcgi -host 127.0.0.1:3033

Then copy sample config to live location:

	user@machine:~/roundware-server$ sudo cp files/apache-config-example /etc/apache2/sites-enabled/000-default

Restart Apache for changes to take effect:

	user@machine:$ sudo /etc/init.d/apache2 restart

## Roundware Installation

Modify the Roundware install script to reflect your codebase location:

	user@machine:~/roundware-server$ vim install_clean_django_rw.sh

Confirm CODE_PATH and DIST_PATH are correct for your system.
Run the `INSTALL-roundware` script (which calls `install_clean_django_rw.sh` among other things):

	user@machine:~/roundware-server$ sh INSTALL-roundware

Give ownership of the log file created in this script to the user who will be running Roundware:

	user@machine: sudo chown [your user] /var/log/roundware

### Configure Django, the python framework Roundware uses.
Reset the Django database by running the resetDb.sh script:

	user@machine:~/roundware-server/roundware$ sh resetDB.sh

*Note - this script may prompt for the username and password for your database.  If you changed these values from the defaults when creating the Roundware db, the changes must be reflected here.*
You'll be asked if you want to create a superuser like so:

	You just installed Django's auth system, which means you don't have any superusers defined.
	Would you like to create one now? (yes/no):

Answer yes, and provide the default values for username ('round') and password ('round').  Note that any subsequent changes must be reflected in `settings.py`.  The email address can be anything, and is not currently used.

If you have a fixture data file, you can populate your database with this data by running the django command:

	user@machine:~/roundware-server/roundware$ python manage.py loaddata <path_to_fixture>

The base Roundware install package includes a standard db fixture file to populate a default database with the basic data you will need to test your installation.  That can be installed similarly, if you so choose:

	user@machine:~/roundware-server/roundware$ python manage.py loaddata rw/fixtures/base_rw.json

Make some edits to the Django settings file, `roundware/settings.py`:

	AUDIO_FILE_URI = "http://roundware.org/audio/" //set to the proper path for your server
	ANONYMOUS_USER_ID = 0 // change this to the proper id for AnonymousUser in database for Guardian
	# settings for notifications module - email account from which notifications will be sent
	EMAIL_HOST = 'smtp.gmail.com'
	EMAIL_HOST_USER = 'email@gmail.com'
	EMAIL_HOST_PASSWORD = 'password'
	EMAIL_PORT = 587
	EMAIL_USE_TLS = True

You are now ready to reset django and run Roundware:

	user@machine:~/roundware-server$ sh install_clean_django_rw.sh
	user@machine:~/roundware-server/roundware$ sh startFCGI.sh

Open a browser and browse to `http://[your hostname]/admin`, and verify you see the django admin page.

Remember, for debugging information, you can check the apache log files:

 * /var/log/apache2/access.log
 * /var/log/apache2/error.log

as well as the Roundware log:

 * /var/log/roundware

## Roundware Development

Roundware uses separate pip requirements files and Django settings files for development.
If you are running Roundware as a development server, you should run:

    user@machine:pip install -r requirements/dev.txt

to get the additional requirements for development and testing.
You should also edit your ~/.bashrc file (or other method of setting user-wide persistent
environment variables) to add:

    export DJANGO_SETTINGS_MODULE=roundware.settings.dev

Note also that you can use a local_settings.py (not in version control) inside
of the roundware/settings/ directory.

## Roundware Config

Roundware has a default config file as well as the option of having project-specific config files.  All Roundware config files are stored by default in `/etc/roundware/` and the default config is at `/etc/roundware/rw`

	# network interface used
	interface = eth0
	# default port for icecast streams
	icecast_port = 8000
	# default location for participant audio (see asset table in db)
	audio_dir = /var/www/rwaudio
	# default location for incoming participant audio - may be used if incoming audio is ingested before included in piece
	upload_dir = /var/www/rwaudio
	# log file location
	log_file = /var/log/roundware
	# process id file
	pid_file = /var/run/roundware.pid
	# database auth
	dbuser = round
	dbpasswd = round
	dbname = roundware
	# settings
	num_pan_steps = 200     	# discrete steps
	stereo_pan_interval = 10      # milliseconds
	ping_interval = 10000   	# milliseconds
	master_volume = 3.0
	# determines connectivity to client.  When client stops beating, session is ended.  Time out in seconds.
	active_stream_check_scheme = heartbeat
	heartbeat_timeout = 200
	# recording radius in meters
	recording_radius = 10
	external_host_name_without_port = http://roundware.org

You need to edit the default config file to change `external_host_name_without_port` to the url of your RW server or else RW will return stream urls with the incorrect server.
You should also go over the other parameters in the config just to make sure they correspond to your setup, such as the database info.

## Roundware Testing


Here are some simple browser tests to see if your Roundware installation is functioning properly (substitute your RW server url):

	http://rw.roundware.org/roundware/?operation=get_config&project_id=1
	http://rw.roundware.org/roundware/?operation=get_tags&session_id=2891
	http://rw.roundware.org/roundware/?operation=request_stream&session_id=2891
	http://rw.roundware.org/roundware/?operation=modify_stream&session_id=2892&tags=3,5,8

The first two should return JSON objects containing information about your Roundware project.  The second two will create and then modify an audio stream.  You can verify stream creation in the Icecast admin, but of course, the true verification is by listening.

To run unit and functional tests and see test coverage, you will need the development requirements (see above).
To run tests and get a report of test coverage:

	user@machine ~/roundware-server/coverage.sh


