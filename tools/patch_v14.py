# -*- coding: utf-8 -*-
"""v14：按键事件附带原始位号，便于反推物理布局。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

# 1) 事件里加位号
old = '''                char k = ttp229_key(m);
                if (k) {
                    g_keys++;
                    g_beep_left = 3;
                    zk_print("ZK|EVT|KEY|%c\\r\\n", k);'''
new = '''                char k = ttp229_key(m);
                if (k) {
                    int bit = -1;
                    for (int bi = 0; bi < 16; bi++) {
                        if (m & (1u << bi)) { bit = bi; break; }
                    }
                    g_keys++;
                    g_beep_left = 3;
                    zk_print("ZK|EVT|KEY|%c|bit=%d|mask=0x%04X\\r\\n", k, bit, m);'''
assert old in s, "按键事件块未找到"
s = s.replace(old, new, 1)

s = s.replace("rk2206-lock-v13", "rk2206-lock-v14")
open(P, "w", encoding="utf-8").write(s)
print("patched v14")
