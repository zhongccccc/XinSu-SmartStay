# -*- coding: utf-8 -*-
"""v60：凭证槽满时淘汰最旧的一条，保证新入住一定能写进去。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

s = s.replace('rk2206-lock-v59', 'rk2206-lock-v60')

OLD = '''        int slot = -1;
        for (int i = 0; i < ZK_CODE_MAX; i++)
        {
            if (g_creds[i].used && strcmp(g_creds[i].code, code) == 0) { slot = i; break; }
            if (!g_creds[i].used && slot < 0) slot = i;
        }'''

NEW = '''        int slot = -1;
        for (int i = 0; i < ZK_CODE_MAX; i++)
        {
            if (g_creds[i].used && strcmp(g_creds[i].code, code) == 0) { slot = i; break; }
            if (!g_creds[i].used && slot < 0) slot = i;
        }
        /* 槽位满了：淘汰序号最小（最旧）的一条，保证新凭证一定写得进去 */
        if (slot < 0) {
            int oldest = 0;
            for (int i = 1; i < ZK_CODE_MAX; i++) {
                if (g_creds[i].seq < g_creds[oldest].seq) oldest = i;
            }
            slot = oldest;
            zk_print("ZK|EVT|CREDEVICT|%s\\r\\n", g_creds[oldest].code);
        }'''

if OLD in s and "CREDEVICT" not in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("已加：槽满淘汰最旧")
else:
    print("状态:", "已存在" if "CREDEVICT" in s else "未匹配")

# 下发成功后回报当前占用数，便于排查
if "ZK|ACK|ISSUE|OK" in s:
    import re
    m = re.search(r'zk_print\("ZK\|ACK\|ISSUE\|OK\|room=%s\|code=%s\\r\\n", argv\[2\], argv\[3\]\);', s)
    if m:
        s = s.replace(m.group(0),
                      'zk_print("ZK|ACK|ISSUE|OK|room=%s|code=%s|slots=%d\\r\\n", argv[2], argv[3], cred_used());', 1)
        # 统计函数
        if "static int cred_used(void)" not in s:
            s = s.replace("static void cred_add(",
                          "static int cred_used(void)\n{\n    int n = 0;\n"
                          "    for (int i = 0; i < ZK_CODE_MAX; i++) if (g_creds[i].used) n++;\n"
                          "    return n;\n}\n\nstatic void cred_add(", 1)
        open(P, "w", encoding="utf-8").write(s)
        print("已加 slots 回报")
