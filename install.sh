#!/bin/bash
# Installer for Roundware Server (http://www.roundware.org/)
# Tested with Ubuntu 12.04 LTS 64 bit

# Enable exit on error
set -e
set -v

# Default MySQL root user password (Change this on a production system!)
MYSQL_ROOT="password"

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
SITE_PACKAGES_PATH="$VENV_PATH/lib/python2.7/site-packages"

# If not vagrant, create user and copy files.
if [ ! "$FOUND_VAGRANT" = true ]; then

  # If user home doesn't exist, create the user.
  if [ ! -d "/home/$USERNAME" ]; then
    useradd $USERNAME -s /bin/bash -m -d $HOME_PATH
  fi

  # If source and dev code paths are different, copy source to code.
  if [ $SOURCE_PATH != $DEV_CODE_PATH ]; then
    rm -rf $DEV_CODE_PATH
    mkdir -p $DEV_CODE_PATH
    cp -R $SOURCE_PATH/. $DEV_CODE_PATH
  fi
fi

# Install/Update the production code
# TODO: Better deployment method.
rm -rf $CODE_PATH
mkdir -p $CODE_PATH
cp -R $SOURCE_PATH/. $CODE_PATH

# Replace the user's .profile
cp $SOURCE_PATH/files/home-user-profile /home/$USERNAME/.profile

# Add a script to start the manage.py runserver development server
cp $SOURCE_PATH/files/home-user-runserver.sh /home/$USERNAME/runserver.sh
chmod 700 /home/$USERNAME/runserver.sh
chown $USERNAME:$USERNAME /home/$USERNAME/runserver.sh

# Create a symbolic link to the main roundware directory
ln -sfn $WWW_PATH /home/$USERNAME/www

# Enable multiverse repository
add-apt-repository "deb http://archive.ubuntu.com/ubuntu $(lsb_release -sc) multiverse"
apt-get update

# Set MySQL root password
echo "mysql-server mysql-server/root_password password $MYSQL_ROOT" | debconf-set-selections
echo "mysql-server mysql-server/root_password_again password $MYSQL_ROOT" | debconf-set-selections

# Install required packages non-interactive
DEBIAN_FRONTEND=noninteractive apt-get install -y python-mysqldb python-configobj mysql-server \
icecast2 ffmpeg apache2 pacpl gstreamer0.10-gnomevfs python-dbus libapache2-mod-wsgi \
python-gst0.10 python-flup gstreamer0.10-ffmpeg gstreamer0.10-fluendo-mp3 \
gstreamer0.10-plugins-base gstreamer0.10-plugins-bad gstreamer0.10-plugins-good \
gstreamer0.10-plugins-bad-multiverse gstreamer0.10-plugins-ugly libavcodec-extra-53 \
python-pip gstreamer-tools python-setuptools python-profiler libmagic1 clamav-daemon \
python-clamav python-lxml python-dev python-pycurl

# Install/upgrade virtualenv
pip install -U virtualenv

# Create the virtual environment
virtualenv --system-site-packages $VENV_PATH

# Activate the environment
source $VENV_PATH/bin/activate
# Set python path to use production code
export PYTHONPATH=$CODE_PATH

# Install upgrade pip
pip install -U pip

# Install RoundWare requirements
pip install -r $CODE_PATH/requirements.txt

# use our configurations for ClamAV
cp $CODE_PATH/files/freshclam.conf /etc/clamav/freshclam.conf
# update ClamAV with latest viruses/malware detection
#freshclam

# Setup MySQL database
echo "create database IF NOT EXISTS roundware;" | mysql -uroot -p$MYSQL_ROOT
echo "grant all privileges on roundware.* to 'round'@'localhost' identified by 'round';" | mysql -uroot -p$MYSQL_ROOT


# File/directory configurations
mkdir -p $MEDIA_PATH
mkdir -p $STATIC_PATH
touch /var/log/roundware
chown $USERNAME:$USERNAME /var/log/roundware
# copy default RW config file into place - don't forget to edit!
mkdir -p /etc/roundware
cp $CODE_PATH/files/sample-config /etc/roundware/rw
# copy test audio file to correct location
cp $CODE_PATH/files/rw_test_audio1.wav $MEDIA_PATH
# install correct shout2send gstreamer plugin
#mv /usr/lib/i386-linux-gnu/gstreamer-0.10/libgstshout2.so /usr/lib/i386-linux-gnu/gstreamer-0.10/libgstshout2.so.old
#cp $CODE_PATH/files/32-bit/libgstshout2.so /usr/lib/i386-linux-gnu/gstreamer-0.10/libgstshout2.so
mv /usr/lib/x86_64-linux-gnu/gstreamer-0.10/libgstshout2.so /usr/lib/x86_64-linux-gnu/gstreamer-0.10/libgstshout2.so.old
cp $CODE_PATH/files/64-bit/libgstshout2.so /usr/lib/x86_64-linux-gnu/gstreamer-0.10/libgstshout2.so

# Install Roundware
python $CODE_PATH/setup.py install
$CODE_PATH/roundware/manage.py collectstatic --noinput

# Set $USERNAME to own all files
chown $USERNAME:$USERNAME -R $HOME_PATH
chown $USERNAME:$USERNAME -R $WWW_PATH

# Initialize database with syncdb and default_auth_data.json
$CODE_PATH/roundware/manage.py syncdb --noinput
$CODE_PATH/roundware/manage.py loaddata $CODE_PATH/roundware/fixtures/default_auth_data.json
$CODE_PATH/roundware/manage.py migrate roundware.rw
$CODE_PATH/roundware/manage.py migrate roundware.notifications
$CODE_PATH/roundware/manage.py migrate guardian
mysql -uroot -p$MYSQL_ROOT roundware < $CODE_PATH/files/rw_base.sql

# TODO: Tastypie migration?

# Setup apache

# Enable Apache rewrite module
a2enmod rewrite
# Enable WSGI module
a2enmod wsgi

rm -f /etc/apache2/sites-available/roundware
ln -s $CODE_PATH/files/apache-config-example-wsgi /etc/apache2/sites-available/roundware
a2ensite roundware
a2dissite 000-default
service apache2 restart

# Setup icecast
cp $CODE_PATH/files/etc-default-icecast2 /etc/default/icecast2
cp $CODE_PATH/files/etc-icecast2-icecast.xml /etc/icecast2/icecast.xml
service icecast2 restart

echo "Done!"
