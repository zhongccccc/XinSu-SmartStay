# -*- coding: utf-8 -*-
"""v36：烧入键盘映射，实现 6 位密码 + # 开门。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

# 1) 默认映射（实测：1→0 3→1 4→2 5→3 6→4 7→5 8→6 9→7 *→8 0→9 #→10，2→11 推断）
old = "static char key_bit[12] = {-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1};"
new = ("/* 实测映射：KEY_ORDER=\"123456789*0#\" */\n"
       "static char key_bit[12] = {0, 11, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10};")
assert old in s
s = s.replace(old, new, 1)

# 2) mask_to_key 改为按"该位对应的字符"返回（保持原逻辑即可，低位优先）
# 3) 每次按键给蜂鸣器反馈，并在串口打印当前已输入的位数
old_key = '''                if (k && k != '?') {
                    g_beep_left = 2;'''
new_key = '''                if (k && k != '?') {
                    g_beep_left = 2;
                    zk_print("ZK|EVT|KEY|%c|len=%d\\r\\n", k, g_pin_len);'''
assert old_key in s
s = s.replace(old_key, new_key, 1)

s = s.replace("rk2206-lock-v35", "rk2206-lock-v36")
open(P, "w", encoding="utf-8").write(s)
print("patched v36")
