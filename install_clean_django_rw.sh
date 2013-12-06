#!/bin/bash
DIST_PATH="/usr/local/lib/python2.7/dist-packages"
CODE_PATH="/home/ubuntu/roundware-server"
FILE_HOME=`dirname $0`
sudo rm -rf $DIST_PATH/roundwared/
sudo rm -rf $DIST_PATH/roundware/
sudo python $FILE_HOME/setup.py install
sudo cp -r $CODE_PATH/roundware/rw/static $DIST_PATH/roundware/rw/
sudo cp -r $CODE_PATH/roundware/rw/templates $DIST_PATH/roundware/rw/
sudo cp -r $CODE_PATH/roundware/notifications/migrations $DIST_PATH/roundware/notifications/migrations
sudo cp -r $CODE_PATH/roundware/rw/migrations $DIST_PATH/roundware/rw/migrations
sudo cp -r $CODE_PATH/roundware/rw/tests $DIST_PATH/roundware/rw/tests
sudo cp -r $CODE_PATH/roundwared/tests $DIST_PATH/roundwared/tests
