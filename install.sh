#!/bin/sh
# Installer for Roundware Server (http://www.roundware.org/)
# Tested with Ubuntu 12.04 LTS

# Enable exit on error
set -e

SOURCE_PATH=`pwd`
CODE_PATH="/home/ubuntu/roundware-server"
INSTALL_PATH="/usr/local/lib/python2.7/dist-packages"
MEDIA_PATH="/var/www/rwmedia"
MYSQL_ROOT="password"

# Enable multiverse repository
add-apt-repository "deb http://archive.ubuntu.com/ubuntu $(lsb_release -sc) multiverse"
apt-get update

echo "mysql-server mysql-server/root_password password $MYSQL_ROOT" | debconf-set-selections
echo "mysql-server mysql-server/root_password_again password $MYSQL_ROOT" | debconf-set-selections

# Install required packages
apt-get install -y python-mysqldb python-configobj mysql-server icecast2 ffmpeg apache2 \
pacpl gstreamer0.10-gnomevfs python-dbus libapache2-mod-wsgi python-gst0.10 python-django \
python-flup gstreamer0.10-ffmpeg gstreamer0.10-fluendo-mp3 gstreamer0.10-plugins-base \
gstreamer0.10-plugins-bad gstreamer0.10-plugins-good gstreamer0.10-plugins-bad-multiverse \
gstreamer0.10-plugins-ugly libavcodec-extra-53 python-pip gstreamer-tools python-setuptools \
python-profiler libmagic1 clamav-daemon python-clamav python-lxml python-dev python-pycurl

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

# Install RoundWare requirements
pip install -r $CODE_PATH/requirements.txt

# use our configurations for ClamAV
cp $SOURCE_PATH/files/freshclam.conf /etc/clamav/freshclam.conf
# update ClamAV with latest viruses/malware detection
freshclam

# Setup MySQL database
echo "create database IF NOT EXISTS roundware;" | mysql -uroot -p$MYSQL_ROOT
echo "grant all privileges on roundware.* to 'round'@'localhost' with grant option;" | mysql -uroot -p$MYSQL_ROOT

mkdir -p /var/www/rwmedia
chown www-data:www-data /var/www/rwmedia
mkdir -p /var/www/.gnome2
chown www-data:www-data /var/www/.gnome2
touch /var/log/roundware
chown www-data /var/log/roundware
mkdir -p /etc/roundware
mkdir -p $CODE_PATH/static
chown www-data $CODE_PATH/static
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

# Setup apache
rm -f /etc/apache2/sites-available/roundware
ln -s $CODE_PATH/files/apache-config-example-wsgi /etc/apache2/sites-available/roundware
a2ensite roundware
service apache2 restart

echo "Done!"

