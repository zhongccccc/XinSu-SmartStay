#!/bin/bash
echo "=== 系统 ==="
uname -m; . /etc/os-release 2>/dev/null; echo "$PRETTY_NAME"
python3 -V

echo
echo "=== Python 依赖 ==="
python3 - <<'PY'
mods = ['numpy', 'cv2', 'onnxruntime', 'yaml', 'PIL']
for m in mods:
    try:
        mod = __import__(m)
        v = getattr(mod, '__version__', '')
        extra = ''
        if m == 'onnxruntime':
            try:
                extra = ' providers=' + ','.join(mod.get_available_providers())
            except Exception as e:
                extra = ' (providers 读取失败)'
        print('  %-12s OK  %s%s' % (m, v, extra))
    except Exception as e:
        print('  %-12s 缺失 (%s)' % (m, type(e).__name__))
PY

echo
echo "=== 摄像头 ==="
ls /dev/video* 2>/dev/null | head -4
ls /opt/zhikong/app/backend/*.json /opt/zhikong/app/*.json 2>/dev/null | head -3

echo
echo "=== 身份证读卡器服务 ==="
curl -s -m 3 'http://127.0.0.1:7846/api/readCard?utf8=1' 2>/dev/null | head -c 200 || echo "  7846 无响应"
echo
ss -lntp 2>/dev/null | grep -E ':7846|:8080' | head -4

echo
echo "=== 串口与磁盘 ==="
ls /dev/ttyUSB* 2>/dev/null
df -h / | tail -1
