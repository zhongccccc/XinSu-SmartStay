#!/bin/bash
echo "===== SYS ====="
uname -a
cat /etc/os-release | head -5
echo "--- cpu ---"
grep -m1 -E 'model name|uarch|isa' /proc/cpuinfo
nproc; free -h | head -2; df -h / | tail -1
echo "--- user ---"
whoami; id
echo
echo "===== USB ====="
which lsusb && lsusb
echo "--- tty ---"
ls -l /dev/ttyUSB* /dev/ttyACM* /dev/ttyS* 2>/dev/null
echo "--- video ---"
ls -l /dev/video* /dev/media* 2>/dev/null
echo "--- input ---"
ls -l /dev/input/by-id/ 2>/dev/null; ls /dev/input/ 2>/dev/null
echo "--- sound ---"
ls -l /dev/snd/ 2>/dev/null
echo "--- i2c/spi/gpio ---"
ls /dev/i2c-* /dev/spidev* /dev/gpiochip* 2>/dev/null
echo "--- rfid/nfc/serial udev ---"
ls /dev/serial/by-id/ 2>/dev/null
echo
echo "===== AUDIO ====="
which arecord aplay pactl wpctl amixer 2>/dev/null
arecord -l 2>&1 | head -20
aplay -l 2>&1 | head -20
echo "--- pactl ---"
pactl info 2>&1 | head -6
pactl list short sinks 2>&1 | head
pactl list short sources 2>&1 | head
echo
echo "===== DISPLAY ====="
echo "DISPLAY=$DISPLAY  WAYLAND=$WAYLAND_DISPLAY  XDG=$XDG_SESSION_TYPE"
ls /dev/dri 2>/dev/null
for f in /sys/class/drm/card*/status; do echo -n "$f: "; cat $f 2>/dev/null; done
ls /sys/class/drm/ 2>/dev/null | head -20
which xrandr weston chromium chromium-browser firefox 2>/dev/null
systemctl is-active lightdm gdm sddm gdm3 2>/dev/null
echo
echo "===== NET ====="
ip -4 addr show | grep -E 'inet |^[0-9]+:'
echo "--- listen ---"
ss -ltnp 2>/dev/null | head -30
echo
echo "===== PY/TOOLS ====="
python3 --version; which python3 pip3 node npm ffmpeg espeak espeak-ng festival mosquitto 2>/dev/null
python3 - <<'EOF'
mods=["cv2","numpy","PIL","pyzbar","serial","sounddevice","pyaudio","flask","fastapi","uvicorn","paho.mqtt","sqlite3","requests","pytesseract","onnxruntime","ncnn"]
import importlib.util as u
for m in mods:
    print(m, bool(u.find_spec(m)))
EOF
echo "===== DOCKER ====="
docker --version 2>&1 | head -2
echo "===== DONE ====="
