#!/bin/bash
set -e
BASE=/home/openharmony/txsmartropenharmony
APP=$BASE/applications/sample/wifi-iot/app/BUILD.gn
MK=$BASE/device/rockchip/rk2206/sdk_liteos/Makefile

# 用厂商 demo 作为唯一 feature
cat > "$APP" <<'EOF'
import("//build/lite/config/component/lite_component.gni")

lite_component("app") {
    features = [
        "//vendor/isoftstone/rk2206/samples/e1_iot_smart_home:iot_smart_home_example",
        "startup",
    ]
}
EOF

# app_LIBS 指向厂商 demo 的库
python3 - "$MK" <<'PY'
import re, sys
mk = sys.argv[1]
m = open(mk).read()
m = re.sub(r'-l(zk_lock|zh_home|iot_smart_home_example)', '-liot_smart_home_example', m)
open(mk, 'w').write(m)
print([l.strip() for l in m.splitlines() if 'app_LIBS' in l])
PY
