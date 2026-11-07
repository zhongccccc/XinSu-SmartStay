#!/bin/bash
echo "=== 服务运行用户 ==="
systemctl cat zhikong-backend 2>/dev/null | grep -E 'User=|Group=|ExecStart=' | head -4
echo
echo "=== 空闲超时值 ==="
grep -n -A8 'def _arm_idle' /opt/zhikong/app/backend/core/model.py | head -14
echo
echo "=== 门锁板掉线恢复逻辑 ==="
grep -n '_use_mock' /opt/zhikong/app/backend/devices/lock.py | head -12
echo
echo "=== 配置里的凭据 ==="
grep -rn 'password\|123456' /opt/zhikong/etc/config.json 2>/dev/null | head -3 || echo "  配置无密码"
echo
echo "=== 脚本里的硬编码密码 ==="
grep -rl '123456' /opt/zhikong/app/scripts/ /opt/zhikong/tools/ 2>/dev/null | head -5
