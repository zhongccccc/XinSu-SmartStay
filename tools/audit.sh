#!/bin/bash
APP=/opt/zhikong/app
echo "=== 代码规模 ==="
find $APP/backend -name '*.py' | wc -l | sed 's/^/  py 文件: /'
find $APP/web -name '*.js' -o -name '*.css' -o -name '*.html' | wc -l | sed 's/^/  web 文件: /'
echo
echo "=== 接口鉴权 ==="
grep -c 'Authorization\|api_key\|token' $APP/backend/main.py || echo "  0（无鉴权）"
echo
echo "=== 空闲超时 ==="
grep -n '_arm_idle\|IDLE' $APP/backend/core/model.py | head -5
echo
echo "=== 日志大小 ==="
ls -lh /opt/zhikong/logs/ 2>/dev/null | head -6
echo
echo "=== 数据库大小 ==="
ls -lh /opt/zhikong/data/*.db 2>/dev/null
echo
echo "=== 测试文件 ==="
find /opt/zhikong -name 'test_*.py' -o -name '*_test.py' 2>/dev/null | head -5 || echo "  无自动化测试"
echo
echo "=== systemd 服务 ==="
systemctl list-units --type=service --state=running 2>/dev/null | grep -i 'zhikong\|idreader' | head -4
