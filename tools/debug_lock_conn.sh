#!/bin/bash
PB=123456
echo "=== 模拟器进程 ==="
pgrep -af lock_board_sim | head -2
echo "=== 链接与设备 ==="
ls -l /tmp/ttyLOCK; ls -l "$(readlink -f /tmp/ttyLOCK)" 2>/dev/null
echo
echo "=== 后端启动时的门锁日志 ==="
grep -E "lock" /opt/zhikong/logs/backend.out | tail -6
echo
echo "=== 以 root 跑一次驱动（后端就是 root）==="
echo "$PB" | sudo -S -p '' python3 /tmp/stl.py 2>&1 | tail -12
