# -*- coding: utf-8 -*-
"""v24：学习模式放宽条件——首次读到非零即记录，并打印原始掩码。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

old = '''        unsigned int last = 0xFFFF;
        unsigned int stable = 0;
        int got = -1;
        unsigned int t0 = now_ms();
        while ((int)(now_ms() - t0) < 10000) {
            unsigned int m = ttp229_read();
            if (m && m == last) {
                stable++;
                if (stable >= 2) {
                    for (int b = 0; b < 16; b++) {
                        if (m & (1u << b)) { got = b; break; }
                    }
                    break;
                }
            } else {
                stable = 0;
            }
            last = m;
            usleep(80 * 1000);
        }'''
new = '''        int got = -1;
        unsigned int t0 = now_ms();
        while ((int)(now_ms() - t0) < 12000) {
            unsigned int m = ttp229_read();
            if (m) {
                zk_print("ZK|LEARN|RAW|%c|0x%04X\\r\\n", want, m);
                for (int b = 0; b < 16; b++) {
                    if (m & (1u << b)) { got = b; break; }
                }
                if (got >= 0) break;
            }
            usleep(30 * 1000);
        }'''
assert old in s, "学习循环未找到"
s = s.replace(old, new, 1)

# 释放等待也放宽
old2 = '''            for (int k = 0; k < 30; k++) {
                if (ttp229_read() == 0) break;
                usleep(80 * 1000);
            }'''
new2 = '''            for (int k = 0; k < 40; k++) {
                if (ttp229_read() == 0) break;
                usleep(50 * 1000);
            }'''
assert old2 in s
s = s.replace(old2, new2, 1)

s = s.replace("rk2206-lock-v23", "rk2206-lock-v24")
open(P, "w", encoding="utf-8").write(s)
print("patched v24")
