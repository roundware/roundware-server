#!/bin/bash

# This script is run to backup the data for roundware from a given host onto the
# machine from which the script is run. This script will install the data into the
# appropriate directories and update the local database to local machine a
# drop-in replacement for the machine it backed up.

# This script is very useful when run as a cron job as frequently as it is
# necessary to back up the data. Running it in a cron job requires that the
# user running it have their ssh client setup with password-less authentication
# using ssh-keygen.

# TODO:
# * Enable the AUDIO_DIR, username, password, and database to be taken from the
#   existing config file on the local machine.
# * Figure out if we want to allow for the src and dst machines to have different
#   config and how to deal with that.

HOST=$1
AUDIO_DIR=/var/www/reconaudio
TEMP=`mktemp /tmp/roundware-mirror.XXXXXX`

/usr/bin/rsync $HOST:$AUDIO_DIR/* $AUDIO_DIR
/usr/bin/ssh $HOST /usr/bin/mysqldump -uround -pround scapes > $TEMP
/bin/cat $TEMP | /usr/bin/mysql -uround -pround scapes
rm $TEMP
/usr/bin/ssh $HOST /usr/bin/mysqldump -uround -pround recon > $TEMP
/bin/cat $TEMP | /usr/bin/mysql -uround -pround recon_backup
rm $TEMP

/usr/bin/ssh $HOST /usr/bin/mysqldump -uround -pround moms > $TEMP
/bin/cat $TEMP | /usr/bin/mysql -uround -pround moms
rm $TEMP