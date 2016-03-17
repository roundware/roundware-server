#!/bin/bash
set -e

# Default to running all tests
TESTS="tests"
if [ -n "$1" ]; then
  TESTS=$1
  echo Running: $TESTS
else
  echo Running All Tests
fi

# runs Django test_coverage script on rw app and roundware-server tests with appropriate settings
cd ..
coverage run --source=roundware,roundwared roundware/manage.py test --settings=roundware.settings.testing $TESTS

# Only display coverage results on full tests
if [ "$TESTS" == "tests" ]; then
  coverage report -m
fi
