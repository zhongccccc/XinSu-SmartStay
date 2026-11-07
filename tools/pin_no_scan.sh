#!/bin/bash
PB=123456
python3 - <<'PY'
import json
p = '/opt/zhikong/etc/config.json'
d = json.load(open(p))
d['devices']['lock']['transport'] = 'board'   # 固定端口，不再扫描（避免打扰板子）
d['devices']['lock']['port'] = '/dev/ttyUSB1'
d['devices']['home_port'] = '/dev/ttyUSB2'
d['devices']['home_sim'] = False
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
print("已固定：lock=ttyUSB1(不扫描)  home=ttyUSB2")
PY
echo "（后端暂不重启，等你把板子断电重启后再起）"
