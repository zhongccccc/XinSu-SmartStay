#!/bin/bash
PB=123456
APP=/opt/zhikong/idreader
CFG=$APP/cfg/idreader.cfg

restart() {
  echo "$PB" | sudo -S -p '' pkill -f qemu-aarch64-static 2>/dev/null
  echo "$PB" | sudo -S -p '' pkill -f id_reader 2>/dev/null
  sleep 1.2
  echo "$PB" | sudo -S -p '' bash -c "setsid $APP/start.sh > $APP/service.out 2>&1 < /dev/null &"
  sleep 5
  curl -s -m 6 "http://127.0.0.1:7846/api/readCard?utf8=1" | tr -d '\n\t ' | head -c 200
  echo
}

for p in 0 1 2 3; do
  echo "=== protocol=$p ==="
  echo "$PB" | sudo -S -p '' python3 - "$p" <<'PY'
import json, sys
p = "/opt/zhikong/idreader/cfg/idreader.cfg"
d = json.load(open(p, encoding="utf-8"))
d["protocol"] = int(sys.argv[1])
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
PY
  restart
done

echo "=== 解绑 usbhid 后（protocol=1）==="
echo "$PB" | sudo -S -p '' python3 - <<'PY'
import json
p = "/opt/zhikong/idreader/cfg/idreader.cfg"
d = json.load(open(p, encoding="utf-8"))
d["protocol"] = 1
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
PY
echo "$PB" | sudo -S -p '' sh -c 'echo 2-1.2.2 > /sys/bus/usb/drivers/usbhid/unbind' 2>/dev/null
ls /dev/hidraw* 2>/dev/null
restart
echo "=== 恢复 usbhid ==="
echo "$PB" | sudo -S -p '' sh -c 'echo 2-1.2.2 > /sys/bus/usb/drivers/usbhid/bind' 2>/dev/null
ls /dev/hidraw* 2>/dev/null
