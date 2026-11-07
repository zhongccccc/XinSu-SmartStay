#!/bin/bash
echo "等待 20 秒，请在此期间按键…"
sleep 20
echo
echo "=== 最近 15 条门锁事件 ==="
grep -a '\[lock\]' /opt/zhikong/logs/backend.out | tail -15
