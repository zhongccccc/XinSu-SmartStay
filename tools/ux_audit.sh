#!/bin/bash
echo "=== 完成页自动返回时间 ==="
grep -n -A10 'def _arm_idle' /opt/zhikong/app/backend/core/model.py | grep -E 'Timer|seconds|IDLE|time' | head -5
grep -n 'IDLE_' /opt/zhikong/app/backend/core/model.py | head -5
echo
echo "=== 待机页元素（客人能看到的按钮）==="
grep -n 'btnStart\|btnCheckoutIdle\|退房\|门锁键盘' /opt/zhikong/app/web/index.html | head -8
echo
echo "=== 完成页元素 ==="
sed -n '/scr-done/,/\/section/p' /opt/zhikong/app/web/index.html | grep -E 'button|id=' | head -8
echo
echo "=== 房卡步骤提示 ==="
grep -n -A4 'scr-card' /opt/zhikong/app/web/index.html | head -12
