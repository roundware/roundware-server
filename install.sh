#!/bin/bash
# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# Installer for Roundware Server (http://www.roundware.org/)
# Tested with Ubuntu 14.04 LTS 64 bit

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
  # Change the user to the vagrant default. (ubuntu, in the case of the 16.04.1 image)
  USERNAME="ubuntu"

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
SITE_PACKAGES_PATH="$VENV_PATH/lib/python2.7/site-packages"

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

# Install required packages non-interactive
DEBIAN_FRONTEND=noninteractive apt-get install -y \
apache2 libapache2-mod-wsgi libav-tools mediainfo pacpl icecast2 \
python-dev python-pip  python-dbus python-gst0.10 \
gstreamer0.10-plugins-good \
gstreamer0.10-tools \
binutils libproj-dev gdal-bin libgdal-dev \
postgresql-server-dev-9.5 postgresql-9.5-postgis-2.2 \
libsidplay1v5

# Download correct port of gstreamer-plugins-ugly/bad, for lame support
# gstreamer0.10-plugins-ugly/bad were removed from Ubuntu 16.04 in favor of gstreamer1.0
# via: https://launchpad.net/ubuntu/xenial/amd64/gstreamer0.10-plugins-ugly/0.10.19-2.1ubuntu4
wget http://launchpadlibrarian.net/225705147/gstreamer0.10-plugins-ugly_0.10.19-2.1ubuntu4_amd64.deb

# via: https://launchpad.net/ubuntu/xenial/amd64/gstreamer0.10-plugins-bad/0.10.23-8.1ubuntu3
wget http://launchpadlibrarian.net/216017741/gstreamer0.10-plugins-bad_0.10.23-8.1ubuntu3_amd64.deb

# install gstreamere-plugins-ugly/bad
dpkg -i gstreamer0.10-plugins-ugly_0.10.19-2.1ubuntu4_amd64.deb
dpkg -i gstreamer0.10-plugins-bad_0.10.23-8.1ubuntu3_amd64.deb

# Install/upgrade virtualenv
pip install -U virtualenv

# Create the virtual environment
virtualenv --system-site-packages $VENV_PATH

# Activate the environment
source $VENV_PATH/bin/activate
# Set python path to use production code
export PYTHONPATH=$CODE_PATH

# Setup Postgresql database
su - postgres -c 'psql -c "create role round superuser login;"'
su - postgres -c 'psql -c "create database roundware"'
su - postgres -c 'psql -c "grant all on database roundware to round"'
su - postgres -c "psql -c \"alter user round password 'round'\""
su - postgres -c "psql roundware -c 'create extension postgis'"

# File/directory configurations
mkdir -p $MEDIA_PATH
mkdir -p $STATIC_PATH

# copy test audio file to media storage
cp $SOURCE_PATH/files/rw_test_audio1.wav $MEDIA_PATH

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

# Install correct shout2send gstreamer plugin
mv /usr/lib/x86_64-linux-gnu/gstreamer-0.10/libgstshout2.so /usr/lib/x86_64-linux-gnu/gstreamer-0.10/libgstshout2.so.old
cp $CODE_PATH/files/64-bit/libgstshout2.so /usr/lib/x86_64-linux-gnu/gstreamer-0.10/libgstshout2.so

# Set $USERNAME to own home files
chown $USERNAME:$USERNAME -R $HOME_PATH

# Setup the default admin account
su - $USERNAME -c "$CODE_PATH/roundware/manage.py loaddata default_auth.json"

# Setup the sample project
su - $USERNAME -c "$CODE_PATH/roundware/manage.py loaddata sample_project.json"

service apache2 restart

# Setup icecast
cp $CODE_PATH/files/etc-default-icecast2 /etc/default/icecast2
cp $CODE_PATH/files/etc-icecast2-icecast.xml /etc/icecast2/icecast.xml
service icecast2 restart

echo "Install Complete"
