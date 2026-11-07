#!/bin/bash
PB=123456
echo "=== 网卡与地址 ==="
ip -br addr 2>/dev/null || ifconfig -a 2>/dev/null | head -30

echo
echo "=== 路由 ==="
ip route 2>/dev/null

echo
echo "=== 默认路由 / DNS ==="
cat /etc/resolv.conf 2>/dev/null | head -5

echo
echo "=== 防火墙 ==="
echo "$PB" | sudo -S -p '' ufw status 2>/dev/null | head -5
echo "--- iptables ---"
echo "$PB" | sudo -S -p '' iptables -L -n 2>/dev/null | head -12

echo
echo "=== 服务监听 ==="
ss -lntp 2>/dev/null | grep -E ':8080|:22|:5901' | head -5

echo
echo "=== IP 转发 ==="
cat /proc/sys/net/ipv4/ip_forward

echo
echo "=== 无线状态 ==="
nmcli -t -f DEVICE,TYPE,STATE,CONNECTION device 2>/dev/null | head -6
