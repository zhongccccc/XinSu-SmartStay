#!/bin/bash
echo "=== ldd ==="
ldd /usr/bin/cam-test 2>/dev/null | head -5
echo "=== 直接运行 10s ==="
timeout 10 cam-test 2>&1 | head -25
echo "=== 运行后 video 节点 ==="
ls /dev/video* | head -8
echo "=== 尝试带配置文件 ==="
timeout 12 cam-test /usr/share/camera_json/csi3_camera_auto.json 2>&1 | head -20
