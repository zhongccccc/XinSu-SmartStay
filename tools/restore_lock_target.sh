#!/bin/bash
set -e
BASE=/home/openharmony/txsmartropenharmony
APP=$BASE/applications/sample/wifi-iot/app/BUILD.gn
MK=$BASE/device/rockchip/rk2206/sdk_liteos/Makefile

cat > "$APP" <<'EOF'
import("//build/lite/config/component/lite_component.gni")

lite_component("app") {
    features = [
        "zhikong_lock:zk_lock",
        "startup",
    ]
}
EOF

python3 - "$MK" <<'PY'
import re, sys
mk = sys.argv[1]
m = open(mk).read()
m = re.sub(r'-l(zk_lock|zh_home|iot_smart_home_example)', '-lzk_lock', m)
open(mk, 'w').write(m)
print([l.strip() for l in m.splitlines() if 'app_LIBS' in l])
PY

echo "已恢复为门锁板目标"
