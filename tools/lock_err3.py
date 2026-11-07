# -*- coding: utf-8 -*-
"""错误/正确提示窗口结束时，主动重绘一次（否则 X 会一直留在屏上）。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

OLD = '''        if (g_oled_ok && g_oled_dirty && t - oled_tick > 150) {'''
NEW = '''        /* 错误/正确提示到期后主动刷新一次 */
        if (g_err_until && (int)(g_err_until - t) <= 0) {
            g_err_until = 0;
            g_oled_dirty = 1;
        }
        if (g_ok_until && (int)(g_ok_until - t) <= 0) {
            g_ok_until = 0;
            g_oled_dirty = 1;
        }

        if (g_oled_ok && g_oled_dirty && t - oled_tick > 150) {'''

if OLD in s and "错误/正确提示到期后主动刷新一次" not in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("已在主循环加到期刷新")
else:
    print("状态:", "已存在" if "错误/正确提示到期后主动刷新一次" in s else "未匹配")
