#!/bin/bash
cd /home/openharmony/txsmartropenharmony/out/rk2206/isoftstone-rk2206 || exit 1

echo "=== 工具链 nm ==="
NM=$(find /home/openharmony/txsmartropenharmony/prebuilts -name 'arm-none-eabi-nm' 2>/dev/null | head -1)
echo "nm = $NM"

echo
echo "=== 我们库里的符号 ==="
if [ -n "$NM" ]; then
  "$NM" libs/libzk_lock.a 2>/dev/null | grep -E ' T | D ' | head -10
fi

echo
echo "=== liteos.elf 里有没有 zk 符号 ==="
if [ -n "$NM" ]; then
  "$NM" liteos.elf 2>/dev/null | grep -i 'zk' | head -10
  echo "符号总数: $("$NM" liteos.elf 2>/dev/null | wc -l)"
fi

echo
echo "=== 链接脚本/映射里的 initcall ==="
ls -la *.map 2>/dev/null | head -3
grep -c 'zk_lock' liteos.map 2>/dev/null || echo "  无 map 文件或未出现"

echo
echo "=== 固件里找字符串 ==="
strings -a liteos.elf 2>/dev/null | grep -E 'lock app ready|ZK.BOOT|rk2206-zk' | head -3
echo "(空=没链接进去)"

echo
echo "=== SYS_RUN 宏定义 ==="
grep -rn 'define SYS_RUN' /home/openharmony/txsmartropenharmony/utils/native/lite/include/ohos_init.h \
     /home/openharmony/txsmartropenharmony/base/startup/*/interfaces/kits/*.h 2>/dev/null | head -3
