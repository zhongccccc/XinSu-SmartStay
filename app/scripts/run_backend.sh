#!/bin/bash
# 启动 K1 网关/一体机后端
set -e
export ZHIKONG_HOME=/opt/zhikong
cd /opt/zhikong/app
exec python3 -u -m backend.main
