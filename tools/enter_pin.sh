#!/bin/bash
B=http://127.0.0.1:8080
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0
PB=123456

CODE=$(curl -s $B/api/state | python3 -c "import sys,json;print(json.load(sys.stdin).get('lock_code') or '')")
echo "当前开门码: $CODE"

tap() { echo "$PB" | sudo -S -p '' python3 /opt/zhikong/app/tools/touch_test.py "$1" "$2" > /dev/null 2>&1; sleep 0.45; }
key() {
  case "$1" in
    1) tap 322 195;; 2) tap 400 195;; 3) tap 477 195;;
    4) tap 322 245;; 5) tap 400 245;; 6) tap 477 245;;
    7) tap 322 297;; 8) tap 400 297;; 9) tap 477 297;;
    0) tap 400 349;; '*') tap 322 349;; '#') tap 477 349;;
  esac
}

echo "=== 清空 ==="
key '*'
sleep 0.5

if [ -n "$CODE" ]; then
  echo "=== 输入 $CODE ==="
  for ((i=0; i<${#CODE}; i++)); do
    d="${CODE:$i:1}"
    key "$d"
  done
  echo "=== 按 # ==="
  key '#'
  sleep 2
fi

grim /tmp/p9.png && echo "shot ok"
echo "=== 门锁日志 ==="
grep -a '\[lock\]' /opt/zhikong/logs/backend.out | tail -6
