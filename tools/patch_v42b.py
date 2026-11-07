# -*- coding: utf-8 -*-
"""v42：把 OLED 刷新/重试真正插进主循环。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

if 'g_oled_dirty &&' in s:
    print("已经存在刷新逻辑，跳过")
    raise SystemExit(0)

anchor = "        n++;\n        if (n % 150 == 0) {"
assert anchor in s, "主循环锚点未找到"

BLOCK = '''        /* ---- OLED：初始化重试 + 内容变化时才刷新 ---- */
        if (!g_oled_ok && g_oled_tries < 8 && t > 2000 && t - oled_tick > 1500) {
            oled_tick = t;
            g_oled_tries++;
            oled_init();
            if (g_oled_ok) {
                zk_print("[zk] oled ok (try %d)\\r\\n", g_oled_tries);
                g_oled_dirty = 1;
            }
        }
        if (g_oled_ok && g_oled_dirty && t - oled_tick > 150) {
            oled_tick = t;
            g_oled_dirty = 0;
            oled_render();
        }

'''
s = s.replace(anchor, BLOCK + anchor, 1)

if 'static volatile int g_oled_tries' not in s:
    s = s.replace('static volatile int g_oled_dirty = 0;   /* 内容变了才刷新 */',
                  'static volatile int g_oled_dirty = 0;   /* 内容变了才刷新 */\n'
                  'static volatile int g_oled_tries = 0;', 1)

s = s.replace("rk2206-lock-v41", "rk2206-lock-v42")
open(P, "w", encoding="utf-8").write(s)
print("patched v42 (main loop render)")
