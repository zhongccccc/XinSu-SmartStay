# -*- coding: utf-8 -*-
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

OLD = """    int slot = -1;
    for (int i = 0; i < ZK_CODE_MAX; i++) {
        if (g_creds[i].used && strcmp(g_creds[i].code, code) == 0) { slot = i; break; }
        if (!g_creds[i].used && slot < 0) slot = i;
    }"""

NEW = """    int slot = -1;
    for (int i = 0; i < ZK_CODE_MAX; i++) {
        if (g_creds[i].used && strcmp(g_creds[i].code, code) == 0) { slot = i; break; }
        if (!g_creds[i].used && slot < 0) slot = i;
    }
    /* 槽位满了：淘汰最旧的一条，保证新入住一定写得进去 */
    if (slot < 0) {
        int oldest = 0;
        for (int i = 1; i < ZK_CODE_MAX; i++) {
            if (g_creds[i].seq < g_creds[oldest].seq) oldest = i;
        }
        slot = oldest;
        zk_print("ZK|EVT|CREDEVICT|%s\\r\\n", g_creds[oldest].code);
    }"""

if "CREDEVICT" not in s and OLD in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("OK: 已加淘汰最旧")
else:
    print("状态:", "已存在" if "CREDEVICT" in s else "未匹配")
