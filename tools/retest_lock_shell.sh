#!/bin/bash
# 用 shell 版模拟器重测：ping / issue / open / revoke
cd /opt/zhikong/app
pkill -f lock_board_sim 2>/dev/null
sleep 0.6
setsid nohup python3 tools/lock_board_sim.py --link /opt/zhikong/run/ttyLOCK > /tmp/sim.log 2>&1 < /dev/null &
sleep 2
head -2 /tmp/sim.log

echo
echo "=== 驱动自测 ==="
python3 /tmp/stl.py 2>&1 | tail -14
