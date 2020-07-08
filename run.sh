#!/bin/sh

echo "starting run.sh"
logger "starting run.sh"
cd /home/pi/GitHub/ping_monitor
./env/bin/python3 ping_test.py 

echo "run.sh complete"
logger "run.sh complete"


