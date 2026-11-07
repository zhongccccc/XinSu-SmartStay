#!/bin/bash
echo "===== BOARD ====="
cat /proc/device-tree/model 2>/dev/null; echo
cat /etc/bianbu-release 2>/dev/null | head -3
echo "===== V4L2 ====="
which v4l2-ctl && v4l2-ctl --list-devices 2>&1 | head -40
for d in /dev/video0 /dev/video50 /dev/video51; do echo "--- $d"; v4l2-ctl -d $d --all 2>&1 | head -12; done
echo "===== INPUT DEVICES ====="
cat /proc/bus/input/devices | sed -n '1,80p'
echo "===== X / SESSION ====="
who; w 2>/dev/null | head -5
ls -l /tmp/.X11-unix/ 2>/dev/null
ps aux | grep -Ei 'vnc|Xorg|wayland|lightdm|sddm|chrom' | grep -v grep
echo "===== SYSTEMD GRAPHICAL ====="
systemctl get-default
systemctl status display-manager --no-pager 2>&1 | head -8
echo "===== NET/PIP ====="
timeout 8 curl -sI https://mirrors.aliyun.com/pypi/simple/ 2>&1 | head -3
timeout 8 curl -sI https://pypi.org/simple/ 2>&1 | head -3
pip3 config list 2>/dev/null
python3 -c "import sys;print(sys.path)"
echo "===== APT ====="
apt-cache policy espeak-ng 2>/dev/null | head -4
echo "===== SUDO ====="
echo 123456 | sudo -S -k true 2>&1 && echo SUDO_OK
echo "===== DONE2 ====="
