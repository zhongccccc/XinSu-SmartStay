#!/bin/bash
PB=123456
for d in /dev/ttyUSB1 /dev/ttyUSB0; do
  for b in 115200 9600; do
    echo "=== $d @ $b ==="
    echo "$PB" | sudo -S -p '' python3 /tmp/sp.py "$d" "$b" 3
  done
done
