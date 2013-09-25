#!/usr/bin/env bash
CODE_PATH="/home/ubuntu/roundware-server"
# update freshclam database each time
sudo freshclam
killall python &&
sh $CODE_PATH/install_clean_django_rw.sh &&
sh $CODE_PATH/roundware/startFCGI.sh &&
sudo apache2ctl restart
