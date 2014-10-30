#!/usr/bin/env python
import commands
import requests

API = "http://localhost:8888/api/1"
ASSET_PATH = '../files/test-audio/'

ASSETS = [
    {'filename': '161700__xserra__ocean-3.mp3',
     'latitude': '1',
     'longitude': '1',
    },
    {'filename': '16937__sculptor__water-submarine.mp3',
     'latitude': '1',
     'longitude': '1',
    },
    {'filename': '243044__phinster__evening-cicadas.mp3',
     'latitude': '1',
     'longitude': '1',
    },
    {'filename': '249887__aguasonic__humpbacks-trk04.mp3',
     'latitude': '1',
     'longitude': '1',
    },
    {'filename': '40807__fresco__thunder-before-rain-by-fresco.mp3',
     'latitude': '1',
     'longitude': '1',
    },
    {'filename': '69663__schaarsen__sfx-nebelhorn.mp3',
      'latitude': '1',
      'longitude': '1',
    },
    {'filename': '74264__lg__rain-02-090612.mp3',
     'latitude': '1',
     'longitude': '1',
    },
    {'filename': '96742__robinhood76__01650-underwater-bubbles.mp3',
     'latitude': '1',
     'longitude': '1',
    },
]

programs = commands.getoutput('ps a')
if 'runserver' in programs:
    print("Django Runserver is running.")
else:
    print("Django Runserver is NOT running, start it.")
    exit(1)

print("Creating a session...")
rconfig = requests.get(API + '/?operation=get_config&project_id=1')
session_id = rconfig.json()[2]['session']['session_id']
print("Session created: %s" % session_id)

print("Creating an envelope...")
renvelope = requests.get(API + '/?operation=create_envelope&session_id=' + str(session_id))
envelope_id = renvelope.json()['envelope_id']
print("Envelope created: %s" % envelope_id)

# Add asset to envelope
for asset in ASSETS:
    print("Uploading an asset: %s" % asset['filename'])
    asset['envelope_id'] = envelope_id
    asset['operation'] = 'add_asset_to_envelope'
    # Use the same tags as the existing demo audio for "gender:male",
    # "question: Why RW?", and "usertype: artist"
    asset['tags'] = "3,5,8"
    files = {'file': open(ASSET_PATH + asset['filename'], 'rb')}
    rasset = requests.post(API + '/?', params=asset, files=files)
    print("Asset created: %s" % rasset.json()['asset_id'])

print("DONE!")

