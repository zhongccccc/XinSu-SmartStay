# -*- coding: utf-8 -*-
"""v37：提交时尝试 12 种位偏移，任一匹配凭证即开锁（对抗帧错位）。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

# 1) 记录原始掩码序列
s = s.replace("static char g_pin[PIN_LEN + 1];",
              "static char g_pin[PIN_LEN + 1];\nstatic unsigned int g_masks[PIN_LEN];   /* 每次按键的原始掩码 */", 1)

# 2) 按键处理：存掩码，不再只存字符
old = '''                    if (k == '#') {
                        g_pin[g_pin_len] = '\\0';
                        int ok = (g_pin_len == PIN_LEN) && cred_check(g_pin);
                        zk_print("ZK|EVT|CODE|%s\\r\\n", ok ? "ok" : "bad");
                        if (ok) do_open("keypad");
                        g_pin_len = 0;
                    } else if (k == '*') {
                        g_pin_len = 0;
                    } else if (g_pin_len < PIN_LEN) {
                        g_pin[g_pin_len++] = k;
                    }'''
new = '''                    if (k == '#') {
                        int ok = 0;
                        char chosen[PIN_LEN + 1];
                        if (g_pin_len == PIN_LEN) {
                            /* 帧可能整体偏移若干位：把 12 种偏移都试一遍 */
                            for (int sh = 0; sh < 12 && !ok; sh++) {
                                for (int p = 0; p < PIN_LEN; p++) {
                                    char c = '?';
                                    for (int bi = 0; bi < 16; bi++) {
                                        if (g_masks[p] & (1u << bi)) {
                                            int want = (bi - sh + 16) % 16;
                                            for (int q = 0; q < 12; q++) {
                                                if (key_bit[q] == want) { c = KEY_ORDER[q]; break; }
                                            }
                                            break;
                                        }
                                    }
                                    chosen[p] = c;
                                }
                                chosen[PIN_LEN] = '\\0';
                                if (cred_check(chosen)) { ok = 1; break; }
                            }
                        }
                        zk_print("ZK|EVT|CODE|%s\\r\\n", ok ? "ok" : "bad");
                        if (ok) do_open("keypad");
                        g_pin_len = 0;
                    } else if (k == '*') {
                        g_pin_len = 0;
                    } else if (g_pin_len < PIN_LEN) {
                        g_masks[g_pin_len] = m;
                        g_pin[g_pin_len] = k;
                        g_pin_len++;
                    }'''
assert old in s, "按键处理片段未找到"
s = s.replace(old, new, 1)

s = s.replace("rk2206-lock-v36", "rk2206-lock-v37")
open(P, "w", encoding="utf-8").write(s)
print("patched v37")
