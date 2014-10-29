#!/bin/bash

# runs Django test_coverage script on rw app and roundware-server tests with appropriate settings
python -3 ../roundware/manage.py test --settings=roundware.settings.testing \
roundware.rw roundware.api1 roundwared
