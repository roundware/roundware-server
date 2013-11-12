#!/bin/bash

# runs Django test_coverage script on rw app with appropriate settings
sh ./install_clean_django_rw.sh
roundware/manage.py test_coverage --settings=roundware.settings.testing rw
