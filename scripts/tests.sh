#!/bin/bash

# runs Django test_coverage script on rw app and roundware-server tests with appropriate settings
cd ../tests
python ../roundware/manage.py test --settings=roundware.settings.testing
