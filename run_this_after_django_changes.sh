#!/usr/bin/env bash
CODE_PATH="/home/ubuntu/rwserver/trunk"
killall python &&
sh $CODE_PATH/install_clean_django_rw.sh &&
sh $CODE_PATH/roundware/startFCGI.sh &&
sudo apache2ctl restart
