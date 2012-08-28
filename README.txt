Roundware 2.0 Installation Guide
--------------------------------

This document will guide you through installing Roundware and its prerequisites.  For further information on Roundware, visit http://www.roundware.org

Assumptions
-----------

- The user is familiar with the bash shell, and has root access to the installation target machine.  The user should be familiar with apache, mysql and icecast.
- The target machine is running Ubuntu 12.04 LTS Precise Pangolin

Unless stated otherwise, all scripts reside in the trunk directory of the Roundware distribution.

Pre-requisites
--------------
Roundware requires many packages to support streaming and management.  Run the INSTALL-prerequisites script to install them:

example:
user@machine:~/rwserver/trunk$ sh INSTALL-prereqs


icecast
-------
Some configuration changes are required to the basic icecast configuration, and they must be in sync with the configured values for Roundware.  We'll mention where these values are configured for Roundware below.  Both of these files must be edited as superuser (sudo).  First, you'll edit the base icecast config. Set the enable value to true.

example: 
sudo vim /etc/default/icecast2

Next, you'll edit the base secondary icecast config. set passwords (in 3 places) to what's in the Roundware configuration file (/etc/roundware/rw, mentioned below).  The default config has the password 'roundice'.  Also, set the max number of sources to 100.

example:
sudo vim /etc/icecast2/icecast.xml

Be sure to restart icecast for these changes to take effect.

example:
sudo /etc/init.d/icecast2 restart

mysql
-----
Roundware requires a dedicated database with a dedicated user.  We can create the default values for this user by running the INSTALL-mysql script.  You'll be prompted 3 times for your mysql root password, which you configured during installation.

example:
user@machine:~/rwserver/trunk$ sh INSTALL-mysql

Of course, you may change the database name and account info to fit your needs, but be sure to change the Roundware config (/etc/roundware/rw) and the django settings (rwserver/trunk/roundware/settings.py) to reflect your changes. 

apache
------
Apache must be configured to forward requests to Roundware fastcgi endpoint.  A default config is included at rwserver/trunk/scripts/apache-config-example.  If installing on a clean 12.04 machine, this file can simply be copied to the apache configuration directory, though there are several changes that should be made to reflect your environment.  Look for the following lines in the apache-config-example, and change them to reflect the location to which you've installed Roundware:

DocumentRoot /home/ubuntu/rwserver/trunk/roundware/

...and towards the bottom...

FastCGIExternalServer /home/ubuntu/rwserver/trunk/roundware/mysite.fcgi -host 127.0.0.1:3033


Now you can copy the sample config:
example:
sudo cp scripts/apache-config-example /etc/apache2/sites-enabled/000-default

Be sure to restart apache for these changes to take effect.

example:
sudo /etc/init.d/apache2 restart


Roundware
---------
1. Run the INSTALL-roundware script
sh INSTALL-roundware

You'll want to give the user running step 4, below, ownership of the log file created in this script, so be sure to modify the following line before running the INSTALL-roundware script:

sudo chown [your user] /var/log/roundware

2. now we'll configure django, the framework Roundware is built upon.  cd to rwserver/trunk/roundware, and reset the django database by running the resetDb script:
sh resetDb.sh

*Note - this script contains username and password for your database.  If you change these values from the defaults when creating the Roundware db, the changes must be reflected here.

You'll be asked if you want to create a superuser like so:
You just installed Django's auth system, which means you don't have any superusers defined.
Would you like to create one now? (yes/no): 


Answer yes, and provide the default values for username ('round') and password ('round').  Note that any subsequent changes must be reflected in settings.py.  The email address can be anything, and is not currently used.

3. If you've received a fixture data file from roundware.org, you can populate your database with this data by running the django command:

python manage.py loaddata path_to_fixture_file from rwserver/trunk/roundware

4. At last you are ready to run Roundware.  
sh startFCGI.sh


Open a browser and browse to http://[your hostname]/admin, and verify you see the django admin page.  Remember, you can check the apache log files (/var/log/apache2/access.log and /var/log/apache2/error.log) as well as the Roundware log (/var/log/roundware) for debugging information.


