#!/bin/bash
# 切换编译目标：lock = 门锁板固件；home = 智能家居板固件
TARGET="$1"
BASE=/home/openharmony/txsmartropenharmony
APP=$BASE/applications/sample/wifi-iot/app
MK=$BASE/device/rockchip/rk2206/sdk_liteos/Makefile

if [ "$TARGET" = "home" ]; then
  LIB="zh_home"
  FEATURE="zhikong_home:zh_home"
elif [ "$TARGET" = "lock" ]; then
  LIB="zk_lock"
  FEATURE="zhikong_lock:zk_lock"
else
  echo "用法: switch_target.sh lock|home"
  exit 1
fi

python3 - "$APP/BUILD.gn" "$FEATURE" "$MK" "$LIB" <<'PY'
import re, sys
gn, feature, mk, lib = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

s = open(gn).read()
s = re.sub(r'"(zhikong_lock:zk_lock|zhikong_home:zh_home)"', '"%s"' % feature, s)
open(gn, 'w').write(s)

m = open(mk).read()
m = re.sub(r'-l(zk_lock|zh_home)', '-l%s' % lib, m)
open(mk, 'w').write(m)

print("features ->", [l.strip() for l in s.splitlines() if 'zhikong' in l])
print("app_LIBS ->", [l.strip() for l in m.splitlines() if 'app_LIBS' in l])
PY
