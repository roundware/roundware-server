#/bin/bash
# Run the Django development server for Roundware on port 8888
pip install -r ~/roundware-server/requirements/dev.txt
~/roundware-server/roundware/manage.py runserver 0.0.0.0:8888 --settings=roundware.settings.dev
# Kill off the rwstreamd.py scripts
killall python
