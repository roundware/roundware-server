#!/bin/bash
# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# Upgrade/Deployment for Roundware Server (http://www.roundware.org/)
# Tested with Ubuntu 14.04 LTS 64 bit
#
# Use this to update production code.

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
fi

# Set paths/directories
WWW_PATH="/var/www/roundware"
CODE_PATH="$WWW_PATH/source"
VENV_PATH="$WWW_PATH"

# Install/Update the production code
# TODO: Better deployment method.
rm -rf $CODE_PATH
mkdir -p $CODE_PATH
cp -R $SOURCE_PATH/. $CODE_PATH

# Activate the environment
source $VENV_PATH/bin/activate
# Set python path to use production code
export PYTHONPATH=$CODE_PATH

# Install upgrade pip
pip install -U pip

# Install RoundWare requirements
pip install -r $CODE_PATH/requirements.txt

# Apply patch to fix M2M field deserializing for Tag relationships, force command to return true.
# Details: https://code.djangoproject.com/ticket/17946
# TODO: Remove when fixed in Django core, probably when upgrading to Django 1.8.
patch -N $WWW_PATH/lib/python2.7/site-packages/django/core/serializers/python.py < $CODE_PATH/files/fix-m2m-deserial.patch || true

# Set $USERNAME to own WWW_PATH files
chown $USERNAME:$USERNAME -R $WWW_PATH

# Run database migrations
su - $USERNAME -c "$CODE_PATH/roundware/manage.py migrate --noinput"

# Collect static files for production
su - $USERNAME -c "$CODE_PATH/roundware/manage.py collectstatic --noinput"

service apache2 restart

echo "Deploy Complete"
