#!/bin/bash

# runs Django test_coverage script on rw app and roundware-server tests with appropriate settings
sh ./install_clean_django_rw.sh
roundware/manage.py test --settings=roundware.settings.testing roundware.rw.tests roundwared.tests
