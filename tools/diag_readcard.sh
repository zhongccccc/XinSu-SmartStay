#!/bin/bash
echo "=== 服务状态 ==="
systemctl is-active idreader
pgrep -af "bin/id_reader" | head -3
echo "=== 端口 ==="
ss -ltnp 2>/dev/null | grep 7846 || echo "未监听"
echo "=== 单次读卡（计时）==="
time curl -s -m 20 'http://127.0.0.1:7846/api/readCard?utf8=1' -o /tmp/one.json
echo "--- 返回 ---"
cat /tmp/one.json 2>/dev/null
echo
echo "=== 最近日志 ==="
journalctl -u idreader --no-pager -n 10 | tail -10
