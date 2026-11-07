#!/bin/bash
PB=123456
echo "$PB" | sudo -S -p '' systemctl reboot
