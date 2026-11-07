#!/bin/bash
cd /opt/zhikong/app
pkill -f lock_board_sim 2>/dev/null
sleep 0.5
setsid nohup python3 tools/lock_board_sim.py --link /tmp/ttyLOCK > /tmp/sim.log 2>&1 < /dev/null &
sleep 2
echo "=== 模拟器日志 ==="
head -3 /tmp/sim.log
echo "=== 链接 ==="
ls -l /tmp/ttyLOCK
echo "=== 进程 ==="
pgrep -af lock_board_sim | head -1
