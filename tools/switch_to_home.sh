#!/bin/bash
cd /home/openharmony/txsmartropenharmony/applications/sample/wifi-iot/app || exit 1
cp -n BUILD.gn BUILD.gn.bak
python3 - <<'PY'
p = '/home/openharmony/txsmartropenharmony/applications/sample/wifi-iot/app/BUILD.gn'
s = open(p).read()
s = s.replace('"zhikong_lock:zk_lock"', '"zhikong_home:zh_home"')
open(p, 'w').write(s)
print("features:", [l.strip() for l in s.splitlines() if 'zhikong' in l])
PY
ls -l /home/openharmony/txsmartropenharmony/applications/sample/wifi-iot/app/zhikong_home/
