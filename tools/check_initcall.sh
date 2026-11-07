#!/bin/bash
cd /home/openharmony/txsmartropenharmony/out/rk2206/isoftstone-rk2206 || exit 1

NM=$(command -v arm-none-eabi-nm)
echo "nm = $NM"
echo
echo "=== 我们的入口函数 ==="
"$NM" liteos.elf | grep -i 'zk_lock_entry\|zk_shell_cmd' | head -5
echo
echo "=== 初始化调用表（SYS_RUN 会在这里挂一项）==="
"$NM" liteos.elf | grep -i 'zinitcall' | head -10
echo
echo "=== 表里成员数量 ==="
"$NM" liteos.elf | grep -c 'zinitcall'
echo
echo "=== .zinitcall 段内容（用 objdump 看）==="
OD=$(command -v arm-none-eabi-objdump)
"$OD" -h liteos.elf 2>/dev/null | grep -i 'zinitcall' | head -6
