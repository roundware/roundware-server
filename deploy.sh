#!/bin/bash
# Upgrade/Deployment for Roundware Server (http://www.roundware.org/)
# Tested with Ubuntu 12.04 LTS 64 bit
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

# Set $USERNAME to own all files
chown $USERNAME:$USERNAME -R $WWW_PATH

# Update database with syncdb and default_auth_data.json
$CODE_PATH/roundware/manage.py syncdb --noinput
$CODE_PATH/roundware/manage.py migrate

# Collect static files for production
$CODE_PATH/roundware/manage.py collectstatic --noinput

service apache2 restart

echo "Deploy Complete"
