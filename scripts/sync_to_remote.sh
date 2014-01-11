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
# * some code taken from: http://bash.cyberciti.biz/backup/backup-mysql-database-server-2/

# set user@server url for RW instance to be backed up
# HOST=$1
HOST=ubuntu@aas.si.edu

# Get data in dd-mm-yyyy format
NOW="$(date +"%m-%d-%Y")"

# Linux bin paths, change this if it can not be autodetected via which command
MYSQL="$(which mysql)"
MYSQLDUMP="$(which mysqldump)"
CHOWN="$(which chown)"
CHMOD="$(which chmod)"
GZIP="$(which gzip)"

# directory on HOST where RW files are stored (full path)
MEDIA_DIR=/var/www/rwmedia

# name backup file with current date
FILE="sirw-backup.$NOW.gz"

#TEMP=`mktemp /tmp/roundware-mirror.XXXXXX`

# rsync from HOST to local directory
/usr/bin/rsync -e "ssh -i /home/halsey/.ssh/id_rsa2" -av --ignore-existing ubuntu@aas.si.edu:/var/www/rwmedia/* rwmedia/
# /usr/bin/rsync $HOST:$MEDIA_DIR/* $MEDIA_DIR

# ssh to remote machine, perform mysqldump and gzip it back to local machine
/usr/bin/ssh -i /home/halsey/.ssh/id_rsa2 $HOST /usr/bin/mysqldump -uround -pround roundware | /bin/gzip -9 > db/$FILE
