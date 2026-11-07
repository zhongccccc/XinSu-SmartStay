# -*- coding: utf-8 -*-
"""v41：重新启用 OLED，但只在内容变化时刷新，且 I2C 失败立刻自禁用。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

# 1) 重新调用 oled_init（延迟到线程里，避开 SYS_RUN 早期）
old = '    /* OLED 暂时禁用：刷新会把板子跑挂，先保证键盘可用 */'
new = '''    /* OLED 初始化放到线程里延后执行，避免开机早期 I2C 未就绪 */
    g_oled_pending = 1;'''
assert old in s
s = s.replace(old, new, 1)

# 2) 加 pending 标志与脏标志
s = s.replace('static volatile int g_oled_ok = 0;',
              'static volatile int g_oled_ok = 0;\n'
              'static volatile int g_oled_pending = 0;\n'
              'static volatile int g_oled_dirty = 0;   /* 内容变了才刷新 */', 1)

# 3) I2C 写失败即禁用
s = s.replace('''        buf[0] = 0x00;
        for (int k = 0; k < m; k++) buf[1 + k] = c[i + k];
        IoTI2cWrite(I2C_OLED, ADDR_OLED, buf, m + 1);''',
              '''        buf[0] = 0x00;
        for (int k = 0; k < m; k++) buf[1 + k] = c[i + k];
        if (IoTI2cWrite(I2C_OLED, ADDR_OLED, buf, m + 1) != IOT_SUCCESS) {
            g_oled_ok = 0;      /* 失败就彻底停用，避免拖死主循环 */
            return;
        }''', 1)

s = s.replace('''        unsigned char buf[33];
        for (int i = 0; i < 128; i += 32) {
            int m = (128 - i > 32) ? 32 : (128 - i);
            buf[0] = 0x40;
            memcpy(buf + 1, &g_fb[page][i], m);
            IoTI2cWrite(I2C_OLED, ADDR_OLED, buf, m + 1);
        }''',
              '''        unsigned char buf[17];
        for (int i = 0; i < 128; i += 16) {
            int m = (128 - i > 16) ? 16 : (128 - i);
            buf[0] = 0x40;
            memcpy(buf + 1, &g_fb[page][i], m);
            if (IoTI2cWrite(I2C_OLED, ADDR_OLED, buf, m + 1) != IOT_SUCCESS) {
                g_oled_ok = 0;
                return;
            }
        }''', 1)

# 4) 渲染触发：按键/开关锁/延迟初始化
s = s.replace('''        /* OLED 渲染已禁用（会导致板子运行一段时间后静默） */''', '''        /* OLED：仅在有变化时刷新，且每 200ms 最多一次 */
        if (g_oled_pending && t > 3000) {
            g_oled_pending = 0;
            oled_init();
            if (g_oled_ok) {
                zk_print("[zk] oled ok\\r\\n");
                g_oled_dirty = 1;
            } else {
                zk_print("[zk] oled init failed\\r\\n");
            }
        }
        if (g_oled_ok && g_oled_dirty && t - oled_tick > 200) {
            g_oled_dirty = 0;
            oled_tick = t;
            oled_render();
        }''', 1)

# 5) 按键、开关锁时置脏
s = s.replace('''                    oled_tick = 0;
                }''', '''                    g_oled_dirty = 1;
                }''', 1)
s = s.replace('''    g_auto_lock_at = now_ms() + AUTO_LOCK_MS;
}''', '''    g_auto_lock_at = now_ms() + AUTO_LOCK_MS;
    g_oled_dirty = 1;
}''', 1)
s = s.replace('''    g_lock_state = 0;
    g_auto_lock_at = 0;
}''', '''    g_lock_state = 0;
    g_auto_lock_at = 0;
    g_oled_dirty = 1;
}''', 1)

# 6) 新增 zk oled 测试命令
anchor = '    } else if (strcmp(sub, "pt") == 0) {'
cmd = '''    } else if (strcmp(sub, "oled") == 0) {
        if (argc > 2 && strcmp(argv[2], "on") == 0) {
            g_oled_pending = 1;
            zk_print("ZK|ACK|OLED|ENABLE\\r\\n");
        } else if (argc > 2 && strcmp(argv[2], "off") == 0) {
            g_oled_ok = 0;
            zk_print("ZK|ACK|OLED|DISABLE\\r\\n");
        } else {
            if (!g_oled_ok) { oled_init(); }
            g_oled_dirty = 1;
            zk_print("ZK|ACK|OLED|%s\\r\\n", g_oled_ok ? "OK" : "FAIL");
        }
'''
if anchor in s and 'ZK|ACK|OLED' not in s:
    s = s.replace(anchor, cmd + anchor, 1)

s = s.replace("rk2206-lock-v40", "rk2206-lock-v41")
open(P, "w", encoding="utf-8").write(s)
print("patched v41")
