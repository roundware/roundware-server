#!/bin/bash
set -e

# runs Django test_coverage script on rw app and roundware-server tests with appropriate settings
cd ..
coverage run --source=roundware,roundwared roundware/manage.py test --settings=roundware.settings.testing tests
coverage report -m
