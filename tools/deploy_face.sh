#!/bin/bash
set -e
SRC=$1     # 本地已解压的 face_verify_k1 目录（在 K1 上的 tar 包路径）
DEST=/opt/zhikong/face
PB=123456

echo "=== 解包到 $DEST ==="
echo "$PB" | sudo -S -p '' mkdir -p "$DEST"
echo "$PB" | sudo -S -p '' tar -xzf "$SRC" -C "$DEST" --strip-components=1
echo "$PB" | sudo -S -p '' chown -R shiqi:shiqi "$DEST"

echo "=== 内容 ==="
ls "$DEST"
echo "  models:"; ls -lh "$DEST/models" | tail -6

echo
echo "=== 依赖是否齐 ==="
python3 -c "import numpy,cv2,onnxruntime,yaml; print('  ok', onnxruntime.__version__)"
