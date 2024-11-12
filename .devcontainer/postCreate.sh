#!/usr/bin/env bash

# install git in our devcontainer
apt-get update -y
apt-get install -y git
apt-get clean
rm -rf /var/lib/apt/lists/*

# migrate the database
python -m roundware.manage migrate

# load fixture data
python -m roundware.manage loaddata default_auth.json
python -m roundware.manage loaddata sample_project.json

