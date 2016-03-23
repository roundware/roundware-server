#!/bin/bash
# Generate new rw and auth fixtures
# Necessary when schema is changed or default data updates are needed
# WARNING: over-writes current default fixtures!
~/roundware-server/roundware/manage.py dumpdata auth.permission auth.user --indent=4 > ~/roundware-server/roundware/rw/fixtures/default_auth.json
~/roundware-server/roundware/manage.py dumpdata rw --indent=4 > ~/roundware-server/roundware/rw/fixtures/sample_project.json
