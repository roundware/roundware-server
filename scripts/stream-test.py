#!/usr/bin/env python
import commands
import requests
import time

try:
    input = raw_input
except NameError:
    pass

API = "http://localhost:8888/api/1"

def move_to(lat,long):
    input("Press Enter to move to (%s,%s), CTRL-C to exit." % (lat,long))
    print("Moving to (%s,%s)" % (lat,long))
    params = {}
    params['operation'] = 'move_listener'
    params['latitude'] = str(lat)
    params['longitude'] = str(long)
    params['session_id'] = "1"
    rmove = requests.get(API + '/', params=params)
    print(rmove.json())
    

programs = commands.getoutput('ps a')
if 'runserver' in programs:
    print("Django Runserver is running.")
else:
    print("Django Runserver is NOT running, start it.")
    exit(1)

print("Creating stream for Session 1")
rstream = requests.get(API + '/?operation=request_stream&project_id=1&session_id=1')
print(rstream.json())

while(True):
    move_to(1,1)
    move_to(1,2)

