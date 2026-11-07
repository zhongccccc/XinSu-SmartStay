#!/bin/bash
PB=123456
echo "=== 已保存的 WiFi 配置 ==="
nmcli -t -f NAME,TYPE connection show 2>/dev/null | head -10

echo
echo "=== 当前 WiFi ==="
nmcli -t -f ACTIVE,SSID,SIGNAL device wifi list 2>/dev/null | grep '^yes' | head -3

echo
echo "=== mDNS（avahi）是否可用 ==="
systemctl is-active avahi-daemon 2>/dev/null || echo "  avahi 未运行"
which avahi-daemon 2>/dev/null || echo "  未安装"
hostname

echo
echo "=== 主机名解析测试 ==="
getent hosts $(hostname).local 2>/dev/null || echo "  .local 解析不到"
