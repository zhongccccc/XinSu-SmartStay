#!/bin/bash
cd /home/openharmony/txsmartropenharmony/out/rk2206/isoftstone-rk2206 || exit 1
echo "=== 哪些 ninja 文件提到 liteos.elf ==="
grep -l 'liteos.elf' *.ninja 2>/dev/null | head -5
echo
echo "=== 链接动作（build 语句） ==="
grep -h -o 'build liteos\.elf[^\\]*' *.ninja 2>/dev/null | head -2
echo
echo "=== 该链接行里的 lib*.a 个数 ==="
grep -h 'liteos.elf' *.ninja 2>/dev/null | tr ' ' '\n' | grep -c '\.a$'
echo
echo "=== 前 40 个输入 ==="
grep -h 'liteos.elf' *.ninja 2>/dev/null | tr ' ' '\n' | grep '\.a$\|\.o$' | head -20
echo
echo "=== 是否含 zk_lock / startup ==="
grep -h 'liteos.elf' *.ninja 2>/dev/null | grep -o 'libzk_lock\|libstartup\|whole-archive\|start-group' | sort | uniq -c
