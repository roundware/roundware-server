#!/bin/bash
# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# Upgrade/Deployment for Roundware Server (http://www.roundware.org/)
# Updated for Python 3.11 and Django 4.2 compatibility
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

cp $SOURCE_PATH/files/home-user-profile /home/$USERNAME/.profile

# Set paths/directories
WWW_PATH="/var/www/roundware"
CODE_PATH="$WWW_PATH/source"
VENV_PATH="/var/www/roundware-venv"  # Updated: venv outside code directory

# Install/Update the production code
# TODO: Better deployment method.
rm -rf $CODE_PATH
mkdir -p $CODE_PATH
cp -R $SOURCE_PATH/. $CODE_PATH

# Create or recreate virtual environment with Python 3.11
if [ -d "$VENV_PATH" ]; then
  echo "Removing existing virtual environment..."
  rm -rf $VENV_PATH
fi

echo "Creating new virtual environment with Python 3.11..."
python3.11 -m venv $VENV_PATH

# Activate the environment
source $VENV_PATH/bin/activate

# Verify Python version
python --version

# Set python path to use production code
export PYTHONPATH=$CODE_PATH

# Install upgrade pip
python -m pip install -U pip wheel setuptools

# Install Roundware requirements (updated path)
if [ -f "$CODE_PATH/requirements/common.txt" ]; then
  echo "Installing from requirements/common.txt..."
  python -m pip install -r $CODE_PATH/requirements/common.txt --upgrade
elif [ -f "$CODE_PATH/requirements.txt" ]; then
  echo "Installing from requirements.txt..."
  python -m pip install -r $CODE_PATH/requirements.txt --upgrade
else
  echo "Error: No requirements file found!"
  exit 1
fi

if [ $ROUNDWARE_DEV ]; then
  python -m pip install -r $CODE_PATH/requirements/dev.txt --upgrade
fi

# Set $USERNAME to own WWW_PATH files
chown $USERNAME:$USERNAME -R $WWW_PATH
chown $USERNAME:$USERNAME -R $VENV_PATH

# Fix venv permissions for package installation
chmod -R u+w $VENV_PATH

# Run database migrations
su - $USERNAME -c "$VENV_PATH/bin/python $CODE_PATH/roundware/manage.py migrate --noinput"

# Collect static files for production
su - $USERNAME -c "$VENV_PATH/bin/python $CODE_PATH/roundware/manage.py collectstatic --noinput"

systemctl restart apache2

echo "Deploy Complete"
