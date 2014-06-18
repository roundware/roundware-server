#!/bin/bash

# runs Django test_coverage script on rw app and roundware-server tests with appropriate settings
roundware/manage.py test --settings=roundware.settings.testing roundware.rw roundwared --pattern="test_*.py"
