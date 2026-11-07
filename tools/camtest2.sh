#!/bin/bash
echo "=== cam-test auto_detect 25s ==="
timeout 25 cam-test /usr/share/camera_json/csi3_camera_detect.json 2>&1 | tail -25
echo
echo "=== 运行后是否多出 video 节点 ==="
ls /dev/video* 2>/dev/null | wc -l
echo "=== 可能的输出文件（近 5 分钟）==="
find /tmp /root /opt -maxdepth 3 -newermt "-5 minutes" -type f 2>/dev/null | grep -viE "\.log$|zhikong" | head -15
