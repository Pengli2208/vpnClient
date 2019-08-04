#!/bin/sh
sudo ifconfig eth0 down
sleep 10
sudo pon pptpconf &
sudo python3 /home/pi/vpnClient/pptpClient.py &

