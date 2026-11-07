#!/bin/bash
PB=123456
mkdir -p /opt/zhikong/data
echo "$PB" | sudo -S -p '' bash -c 'setsid python3 /opt/zhikong/app/tools/hid_probe.py dump /dev/hidraw2 240 > /opt/zhikong/data/idcap.out 2>&1 < /dev/null &'
sleep 1
pgrep -af "hid_probe.py dump" | head -2
echo "capture started (240s)"
