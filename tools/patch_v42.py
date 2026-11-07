# -*- coding: utf-8 -*-
"""v42：OLED 开机初始化失败自动重试；按键时若未就绪也会重试。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

# 1) 重试计数
s = s.replace('static volatile int g_oled_dirty = 0;   /* 内容变了才刷新 */',
              'static volatile int g_oled_dirty = 0;   /* 内容变了才刷新 */\n'
              'static volatile int g_oled_tries = 0;', 1)

# 2) 初始化重试逻辑（每 2 秒试一次，最多 8 次）
old = '''        if (g_oled_pending && t > 3000) {
            g_oled_pending = 0;
            oled_init();
            if (g_oled_ok) {
                zk_print("[zk] oled ok\\r\\n");
                g_oled_dirty = 1;
            } else {
                zk_print("[zk] oled init failed\\r\\n");
            }
        }'''
new = '''        if (!g_oled_ok && g_oled_tries < 8 && t > 3000 && t - oled_tick > 2000) {
            oled_tick = t;
            g_oled_tries++;
            oled_init();
            if (g_oled_ok) {
                zk_print("[zk] oled ok (try %d)\\r\\n", g_oled_tries);
                g_oled_tries = 100;
                g_oled_dirty = 1;
            } else if (g_oled_tries == 1 || g_oled_tries % 3 == 0) {
                zk_print("[zk] oled retry %d\\r\\n", g_oled_tries);
            }
        }'''
assert old in s
s = s.replace(old, new, 1)

# 3) 按键时若 OLED 未就绪，允许再试一次
s = s.replace('''                if (k && k != '?') {
                    g_beep_left = 2;''',
              '''                if (k && k != '?') {
                    if (!g_oled_ok && g_oled_tries < 20) {
                        g_oled_tries++;
                        oled_init();
                    }
                    g_beep_left = 2;''', 1)

s = s.replace("rk2206-lock-v41", "rk2206-lock-v42")
open(P, "w", encoding="utf-8").write(s)
print("patched v42")
