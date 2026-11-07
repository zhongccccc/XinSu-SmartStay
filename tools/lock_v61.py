# -*- coding: utf-8 -*-
"""v61 = v58 行为 + 仅"密码错误提示"（去掉槽位淘汰、去掉 slots 回报）。"""
import re

P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

# 1) 去掉槽位淘汰
OLD_EVICT = """    /* 槽位满了：淘汰最旧的一条，保证新入住一定写得进去 */
    if (slot < 0) {
        int oldest = 0;
        for (int i = 1; i < ZK_CODE_MAX; i++) {
            if (g_creds[i].seq < g_creds[oldest].seq) oldest = i;
        }
        slot = oldest;
        zk_print("ZK|EVT|CREDEVICT|%s\\r\\n", g_creds[oldest].code);
    }
"""
if OLD_EVICT in s:
    s = s.replace(OLD_EVICT, "", 1)
    print("[1] 已去掉槽位淘汰")
else:
    print("[1] 未找到淘汰代码")

# 2) ACK 去掉 slots
s = s.replace('zk_print("ZK|ACK|ISSUE|OK|room=%s|code=%s|slots=%d\\r\\n", argv[2], argv[3], cred_used());',
              'zk_print("ZK|ACK|ISSUE|OK|room=%s|code=%s\\r\\n", argv[2], argv[3]);')
print("[2] ACK 已恢复原样")

# 3) 版本号
s = re.sub(r'#define ZK_VER\s+"[^"]+"', '#define ZK_VER           "rk2206-lock-v61"', s, count=1)
if "rk2206-lock-v61" not in s:
    s = s.replace('rk2206-lock-v60', 'rk2206-lock-v61')
print("[3] 版本:", [l.strip() for l in s.splitlines() if "ZK_VER" in l and "define" in l])

open(P, "w", encoding="utf-8").write(s)

# 4) 确认错误提示还在
print("[4] 错误提示代码:", "在" if "g_err_until" in s else "缺失!")
print("[5] cred_used 是否仍被引用:", s.count("cred_used"))
