# ROUNDWARE INSTALLATION GUIDE
## Overview

Roundware is a client-server system. The server runs using Apache HTTP Server and mod_wsgi on Ubuntu Linux 12.04 LTS Precise Pangolin and clients are available for iOS, Android and HTML5 browsers. This document outlines the steps required to setup a basic Roundware server that can be accessed through any of these clients.

For more information about Roundware functionalities and projects that use the platform, please check out: [roundware.org](http://roundware.org "Roundware")

## Basic Installation

Roundware includes an *install.sh* to handle installation of the software and its dependencies. The majority of the process is automated. Further configuration is required for a production system, application specific details are below.

    user@server:~ $ git clone https://github.com/hburgund/roundware-server.git
    user@server:~ $ cd roundware-server
    user@server:~/roundware-server $ sudo ./install.sh

The installation process creates a *roundware* user as project owner. su to that user to load the required virtual environment:

    sudo su - roundware

## Vagrant

A VagrantFile is included for local development and testing with [Vagrant](http://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/). Usage:

    user@local-machine:~ $ git clone https://github.com/hburgund/roundware-server.git
    user@local-machine:~ $ cd roundware-server
    user@local-machine:~/roundware-server $ vagrant up
    user@local-machine:~/roundware-server $ vagrant ssh
    (roundware)vagrant@roundware-server:~$ ./runserver.sh

Notes:

 * The installation process uses the default *vagrant* user as project owner.
 * The install script relies on the Vagrant default fileshare of host:~/roundware-server to vm:/vagrant for installation and development.
 * There are multiple port forwards from the host to the VM:
   * VM:80->host:8080 for Apache hosting the demo "live" environment available at http://127.0.0.1:8080/
   * VM:8888->host:8888 for the manage.py runserver development webserver available at http://127.0.0.1:8888/
   * VM:8000->host:8000 for Icecast.
 * Initialize the test Roundware stream at: http://127.0.0.1:8888/roundware/?operation=request_stream&session_id=1 then access it with an audio stream player at: http://127.0.0.1:8000/stream1.mp3
 * Edit the development environment code on your local machine, then refresh to see the changes reflected in the virtual machine.

## Icecast

Roundware uses Icecast to stream audio, much like internet radio stations. If Icecast is manually installed, it will require some configuration to function properly with Roundware. The configuration changes must be in sync with the configured values for Roundware. Sample Icecast config files are included in the distribution in the `roundware-server/files` directory.

Edit the base Icecast config:

    user@machine:$ sudo vim /etc/default/icecast2

Set/verify the enable value to true:

    ENABLE=true

Next, you'll edit the general Icecast config:

    user@machine:$ sudo vim /etc/icecast2/icecast.xml

Set passwords (in 3 places) to correspond with what is in the Roundware default configuration, currently set in `roundwared/settings.py`. You may have already been prompted for these passwords during the Icecast install process, in which case you should simply verify that they are in the XML. The default config has the password 'roundice'. Also, set the max number of sources to 100.

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

To verify that icecast is up and running go to `http://example.com:8000` to see the default Icecast admin page.

## MySQL

Roundware uses MySQL and requires a dedicated database with a dedicated user.

You may change the database name and account info to fit your needs, but if you do, be sure to change the Roundware config (`/etc/roundware/rw`) and the Django settings (`roundware-server/roundware/settings.py`) to reflect your changes.

## Apache

Apache must be configured to use [mod_wsgi](http://www.modwsgi.org) to host Roundware. A default config is included at `roundware-server/files/apache-config-example-wsgi`. If manually installing on a clean 12.04 machine, this file can simply be copied to the Apache configuration directory, though there are several changes that should be made to reflect your environment.

### Configure Django, the Python framework Roundware uses.

    (roundware)user@machine:~/roundware-server/roundware$ ./manage.py syncdb

*Note - this script may prompt for the username and password for your database. If you changed these values from the defaults when creating the Roundware DB, the changes must be reflected here.*
You'll be asked if you want to create a superuser like so:

    You just installed Django's auth system, which means you don't have any superusers defined.
    Would you like to create one now? (yes/no):

Answer yes, and provide the default values for username ('round') and password ('round'). Note that any subsequent changes must be reflected in `settings.py`. The email address can be anything, and is not currently used.

If you have a fixture data file, you can populate your database with this data by running the Django command:

    (roundware)user@machine:~/roundware-server/roundware$ ./manage.py loaddata <path_to_fixture>

The base Roundware install package includes a standard DB fixture file to populate a default database with the basic data you will need to test your installation. That can be installed similarly, if you so choose:

    (roundware)user@machine:~/roundware-server/roundware$ ./manage.py loaddata rw/fixtures/base_rw.json

Make some edits to the Django settings file, `roundware/settings.py`:

    AUDIO_FILE_URI = "http://example.com/audio/" //set to the proper path for your server
    ANONYMOUS_USER_ID = 0 // change this to the proper id for AnonymousUser in database for Guardian
    # settings for notifications module - email account from which notifications will be sent
    EMAIL_HOST = 'smtp.example.com'
    EMAIL_HOST_USER = 'email@example.com'
    EMAIL_HOST_PASSWORD = 'password'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

Open a browser and browse to `http://example.com/admin`, and verify you see the Django admin page.

You can check the Apache log files for debugging information:

 * /var/log/apache2/access.log
 * /var/log/apache2/error.log

as well as the Roundware log:

 * /var/log/roundware

## Roundware Development

Roundware uses separate pip requirements files and Django settings files for development.
If you are running Roundware as a development server, you should run:

    user@machine:~/roundware-server $ pip install -r requirements/dev.txt

to get the additional requirements for development and testing.
You should also edit your ~/.bashrc file (or other method of setting persistent
environment variables) to add:

    export DJANGO_SETTINGS_MODULE=roundware.settings.dev

Note also you can use a local_settings.py (not in version control) inside
of the roundware/settings/ directory.

## Roundware Config

All Roundware specific settings are stored in roundware/settings/common.py

## Roundware Testing

Here are some simple browser tests to see if your Roundware installation is functioning properly (substitute your RW server url):

    http://example.com/roundware/?operation=get_config&project_id=1
    http://example.com/roundware/?operation=get_tags&session_id=1
    http://example.com/roundware/?operation=request_stream&session_id=1
    http://example.com/roundware/?operation=modify_stream&session_id=1

The first two should return JSON objects containing information about your Roundware project. The second two will create and then modify an audio stream. You can verify stream creation in the Icecast admin, but of course, the true verification is by listening.

To run unit and functional tests and see test coverage, you will need the development requirements (see above).
To run tests and get a report of test coverage:

    user@machine ~/roundware-server/coverage.sh
