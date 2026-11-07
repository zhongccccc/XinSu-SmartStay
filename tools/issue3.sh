#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' systemctl stop zhikong-backend 2>/dev/null
sleep 1
echo "$PB" | sudo -S -p '' python3 /tmp/probe_issue.py
echo "$PB" | sudo -S -p '' systemctl start zhikong-backend
sleep 6
echo "backend: $(systemctl is-active zhikong-backend)"
