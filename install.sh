#!/bin/bash
# Installer for Roundware Server (http://www.roundware.org/)
# Tested with Ubuntu 12.04 LTS

# Enable exit on error
set -e

PROJECT="roundware-server"
SOURCE_PATH=`pwd`
CODE_PATH="/home/ubuntu/roundware-server"
VENV_PATH="/usr/pythonenv"
INSTALL_PATH="$VENV_PATH/$PROJECT/lib/python2.7/site-packages"
MEDIA_PATH="/var/www/rwmedia"
MYSQL_ROOT="password"

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

# Enable Apache rewrite module
a2enmod rewrite
# Enable WSGI module
a2enmod wsgi

# Copy the entire code base to the code path
if [ $SOURCE_PATH != $CODE_PATH ]; then
  rm -rf $CODE_PATH
  mkdir -p $CODE_PATH
  cp -R $SOURCE_PATH/. $CODE_PATH
fi

# Install upgrade virtualenv
pip install -U virtualenv

# Create the pythonenv directory
mkdir -p $VENV_PATH

# Create the virtual environment
cd $VENV_PATH
virtualenv --system-site-packages $PROJECT

# Activate the environment
source $VENV_PATH/$PROJECT/bin/activate

# Install upgrade pip
pip install -U pip

# Install RoundWare requirements
pip install -r $CODE_PATH/requirements.txt

# use our configurations for ClamAV
cp $SOURCE_PATH/files/freshclam.conf /etc/clamav/freshclam.conf
# update ClamAV with latest viruses/malware detection
#freshclam

# Setup MySQL database
echo "create database IF NOT EXISTS roundware;" | mysql -uroot -p$MYSQL_ROOT
echo "grant all privileges on roundware.* to 'round'@'localhost' identified by 'round';" | mysql -uroot -p$MYSQL_ROOT


# File/directory configurations
mkdir -p /var/www/rwmedia
chown ubuntu:ubuntu /var/www/rwmedia
touch /var/log/roundware
chown ubuntu:ubuntu /var/log/roundware
mkdir -p /etc/roundware
mkdir -p $CODE_PATH/static
chown www-data:www-data $CODE_PATH/static
# copy default RW config file into place - don't forget to edit!
cp $CODE_PATH/files/sample-config /etc/roundware/rw
# copy test audio file to correct location
cp $CODE_PATH/files/rw_test_audio1.wav /var/www/rwmedia
# install correct shout2send gstreamer plugin
#mv /usr/lib/i386-linux-gnu/gstreamer-0.10/libgstshout2.so /usr/lib/i386-linux-gnu/gstreamer-0.10/libgstshout2.so.old
#cp $CODE_PATH/files/32-bit/libgstshout2.so /usr/lib/i386-linux-gnu/gstreamer-0.10/libgstshout2.so
mv /usr/lib/x86_64-linux-gnu/gstreamer-0.10/libgstshout2.so /usr/lib/x86_64-linux-gnu/gstreamer-0.10/libgstshout2.so.old
cp $CODE_PATH/files/64-bit/libgstshout2.so /usr/lib/x86_64-linux-gnu/gstreamer-0.10/libgstshout2.so

# Install Roundware to $INSTALL_PATH
rm -rf $INSTALL_PATH/roundwared/
rm -rf $INSTALL_PATH/roundware/
cd $CODE_PATH
python setup.py install
cp -r $CODE_PATH/roundware/rw/static $INSTALL_PATH/roundware/rw/
cp -r $CODE_PATH/roundware/rw/templates $INSTALL_PATH/roundware/rw/
cp -r $CODE_PATH/roundware/notifications/migrations $INSTALL_PATH/roundware/notifications/migrations
cp -r $CODE_PATH/roundware/rw/migrations $INSTALL_PATH/roundware/rw/migrations
cp -r $CODE_PATH/roundware/rw/tests $INSTALL_PATH/roundware/rw/tests
cp -r $CODE_PATH/roundwared/tests $INSTALL_PATH/roundwared/tests
$CODE_PATH/roundware/manage.py collectstatic --noinput

# Initialize database with syncdb and default_auth_data.json
$CODE_PATH/roundware/manage.py syncdb --noinput
$CODE_PATH/roundware/manage.py loaddata $CODE_PATH/roundware/fixtures/default_auth_data.json
$CODE_PATH/roundware/manage.py migrate roundware.rw
$CODE_PATH/roundware/manage.py migrate roundware.notifications
# TODO: Other migrations?

# Setup apache
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
