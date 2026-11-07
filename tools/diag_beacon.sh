#!/bin/bash
B=http://127.0.0.1:8080
echo "=== beacon 接口是否还在 ==="
curl -s -m 4 -X POST -H 'Content-Type: application/json' -d '{"x":1,"y":2,"type":"probe","ev":"probe"}' $B/api/debug/click
echo
echo "=== 输入设备（看有没有残留的虚拟触摸）==="
for e in /dev/input/event*; do
  n=$(cat /sys/class/input/${e##*/}/device/name 2>/dev/null)
  case "$n" in
    *zhikong*) echo "  残留: $e $n" ;;
  esac
done
echo "  (无输出=无残留)"
echo
echo "=== chromium 进程 ==="
pgrep -af "chromium.*8080" | head -3
echo
echo "=== 当前状态 ==="
curl -s $B/api/state | python3 -c "import sys,json;d=json.load(sys.stdin);print('  step=',d['step'])"
