#!/bin/bash
# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# Installer for Roundware Server (http://www.roundware.org/)
# Tested with Ubuntu 18.04 LTS 64 bit

# Enable exit on error
set -e
set -v

# Store the script start path
SOURCE_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if we are installing via vagrant (assuming standard Vagrant /vagrant share)
if [ -d "/vagrant" ]; then
  echo "Found Vagrant."
  FOUND_VAGRANT=true
fi

# Default user name.
USERNAME="roundware"

# Use vagrant username/directories used when available.
if [ "$FOUND_VAGRANT" = true ]; then
  # Change the user to the vagrant default.
  USERNAME="vagrant"

  # Create a symbolic link in the user's directory to the code
  ln -sfn /vagrant /home/$USERNAME/roundware-server
fi

# Set paths/directories
HOME_PATH="/home/$USERNAME"
DEV_CODE_PATH="$HOME_PATH/roundware-server"

WWW_PATH="/var/www/roundware"
CODE_PATH="$WWW_PATH/source"
STATIC_PATH="$WWW_PATH/static"
MEDIA_PATH="$WWW_PATH/rwmedia"
VENV_PATH="$WWW_PATH"

# If not vagrant, create user and copy files.
if [ ! "$FOUND_VAGRANT" = true ]; then

  # If user home doesn't exist, create the user.
  if [ ! -d "/home/$USERNAME" ]; then
    useradd $USERNAME -s /bin/bash -m -d $HOME_PATH
  fi

  # If source and dev code paths are different, create a symbolic link to code.
  if [ $SOURCE_PATH != $DEV_CODE_PATH ]; then
    rm -rf $DEV_CODE_PATH
    ln -sfn $CODE_PATH $DEV_CODE_PATH
  fi
fi

# Replace the user's .profile
cp $SOURCE_PATH/files/home-user-profile /home/$USERNAME/.profile

# Create a symbolic link to the main roundware directory
ln -sfn $WWW_PATH /home/$USERNAME/www

apt-get update
# Install packages for running Roundware Server
xargs -a requirements.apt sudo apt-get install -y
# Install additional packages for running Postgres locally
DEBIAN_FRONTEND=noninteractive apt-get install -y postgresql postgis
# Install virtualenv
DEBIAN_FRONTEND=noninteractive apt-get install -y python3-venv
python3 -m pip install pip --upgrade
# Install additional packages for running apache
DEBIAN_FRONTEND=noninteractive apt-get install -y apache2 apache2-dev libapache2-mod-wsgi-py3
python3 -m pip install mod_wsgi

# Create the virtual environment
python3 -m venv $VENV_PATH

# Activate the environment
# shellcheck disable=SC1090
source $VENV_PATH/bin/activate
# Set python path to use production code
export PYTHONPATH=$CODE_PATH

# Setup Postgresql database
if ! su - postgres -c "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='round'\"" | grep -q 1; then
  su - postgres -c 'psql -c "create role round superuser login;"'
fi

if ! su - postgres -c "psql -lqt" | cut -d \| -f 1 | grep -qw 'roundware'; then
  su - postgres -c 'psql -c "create database roundware"'
fi

su - postgres -c 'psql -c "grant all on database roundware to round"'
su - postgres -c "psql -c \"alter user round password 'round'\""

# File/directory configurations
mkdir -p $MEDIA_PATH
mkdir -p $STATIC_PATH

# copy test audio file to media storage
cp $SOURCE_PATH/files/rw_test_audio1.wav $MEDIA_PATH
cp $SOURCE_PATH/files/rw_test_audio1.mp3 $MEDIA_PATH

# Copy default production settings file
mkdir -p $WWW_PATH/settings
cp $SOURCE_PATH/files/var-www-roundware-settings.py $WWW_PATH/settings/roundware_production.py

# Setup roundware log and logrotate
touch /var/log/roundware
chown $USERNAME:$USERNAME /var/log/roundware

# Run the production upgrade/deployment script
$SOURCE_PATH/deploy.sh

# Setup Apache Server
a2enmod rewrite
a2enmod wsgi
a2enmod headers
a2dissite 000-default
# Setup roundware in Apache
rm -f /etc/apache2/sites-available/roundware.conf
sed s/USERNAME/$USERNAME/g $CODE_PATH/files/etc-apache2-sites-available-roundware > /etc/apache2/sites-available/roundware.conf
a2ensite roundware

# Setup logrotate
sed s/USERNAME/$USERNAME/g $CODE_PATH/files/etc-logrotate-d-roundware > /etc/logrotate.d/roundware

# Set $USERNAME to own home files
chown $USERNAME:$USERNAME -R $HOME_PATH

# Setup the default admin account
su - $USERNAME -c "$CODE_PATH/roundware/manage.py loaddata default_auth.json"

# Setup the sample project
su - $USERNAME -c "$CODE_PATH/roundware/manage.py loaddata sample_project.json"

service apache2 restart

echo "Install Complete"
