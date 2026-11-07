#!/bin/bash
echo "=== csi3_camera_auto.json ==="
cat /usr/share/camera_json/csi3_camera_auto.json
echo
echo "=== csi3_camera_detect.json (前 40 行) ==="
head -40 /usr/share/camera_json/csi3_camera_detect.json
echo
echo "=== cam-test 用法线索 ==="
strings /usr/bin/cam-test | grep -iE "usage|\.json|auto|csi[0-9]|argv|option" | head -25
