#!/bin/bash
# Run the Django development server for Roundware on port 8888
python3 -m pip install -r ~/roundware-server/requirements/dev.txt

python3 ~/roundware-server/roundware/manage.py runserver 0.0.0.0:8888 --settings=roundware.settings.dev
# Kill off the rwstreamd.py scripts
killall python3

