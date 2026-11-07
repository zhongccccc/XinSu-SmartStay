#!/bin/bash
PB=123456
echo "=== 1. 现有配置 ==="
ls -l /tmp/csi*_camera_auto.json /usr/share/camera_json/*.json 2>/dev/null
echo
echo "=== 2. 重新识别（放到 /tmp）==="
echo "$PB" | sudo -S -p '' cam-test /usr/share/camera_json/csi3_camera_detect.json 2>&1 | grep -E "detect imx219|success|save json" | tail -3
ls -l /tmp/csi3_camera_auto.json 2>/dev/null
echo
echo "=== 3. 生成 svivi 配置并加 use_v4l ==="
echo "$PB" | sudo -S -p '' cp /tmp/csi3_camera_auto.json /root/svivi_cam1.json 2>/dev/null
echo "$PB" | sudo -S -p '' python3 - <<'PY'
import json
p = "/root/svivi_cam1.json"
d = json.load(open(p, encoding="utf-8"))
d["use_v4l"] = 1
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("use_v4l =", d.get("use_v4l"), "| sensor:", d["isp_node"][0].get("sensor_name"))
PY
echo "$PB" | sudo -S -p '' python3 -m json.tool /root/svivi_cam1.json > /dev/null && echo CONFIG_OK
echo
echo "=== 4. gstreamer 插件 ==="
which gst-inspect-1.0
gst-inspect-1.0 spacemitsrc 2>&1 | head -6
echo
echo "=== 5. video 节点 ==="
ls -l /dev/video50 /dev/video51 2>/dev/null
