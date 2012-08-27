#!/bin/bash
RUNDIR=`dirname $0`
python $RUNDIR/manage.py runfcgi method=threaded host=127.0.0.1 port=3033
