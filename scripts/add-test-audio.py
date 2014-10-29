#!/usr/bin/env python
API = "http://localhost:8888/api/1"

import commands
import requests

programs = commands.getoutput('ps a')
if 'runserver' in programs:
    print("Django Runserver is running.")
else:
    print("Django Runserver is NOT running, start it.")

print("Creating a session...")
rgetconfig = requests.get(API + '/?operation=get_config&project_id=1')
session_id = rgetconfig.json()[2]['session']['session_id']
print("Session created: %s" % session_id)

print("Creating an envelope...")
renvelope = requests.get(API + '/?operation=create_envelope&session_id=' + str(session_id))
envelope_id = renvelope.json()['envelope_id']
print("Envelope created: %s" % envelope_id)

# Add asset to envelope


