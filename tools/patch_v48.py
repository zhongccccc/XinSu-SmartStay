# -*- coding: utf-8 -*-
"""v48：蜂鸣器改为固定短音；OLED 刷新提速；NFC 轮询不再长时间阻塞。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

# 1) 蜂鸣器改为时间截止制
s = s.replace('static volatile int g_beep_left = 0;',
              'static volatile unsigned int g_beep_until = 0;')

s = s.replace('''        if (g_beep_left > 0 && g_pwm_ready) {
            if (!g_beep_on) { IoTPwmStart(PWM_BUZZER, 50, 2700); g_beep_on = 1; }
            g_beep_left--;
        } else if (g_beep_on) {
            IoTPwmStop(PWM_BUZZER);
            g_beep_on = 0;
        }''',
              '''        if (g_beep_until && (int)(g_beep_until - t) > 0 && g_pwm_ready) {
            if (!g_beep_on) { IoTPwmStart(PWM_BUZZER, 50, 2700); g_beep_on = 1; }
        } else if (g_beep_on) {
            IoTPwmStop(PWM_BUZZER);
            g_beep_on = 0;
            g_beep_until = 0;
        }''', 1)

s = s.replace('    g_beep_left = 6;', '    g_beep_until = now_ms() + 90;   /* 开锁提示音：短促 */', 1)
s = s.replace('    g_beep_left = 4;', '    g_beep_until = now_ms() + 90;', 1)
s = s.replace('                    g_beep_left = 2;', '                    g_beep_until = now_ms() + 35;   /* 按键：极短 */', 1)
s = s.replace('            g_beep_left = 2;', '            g_beep_until = now_ms() + 35;', 1)

# 2) OLED 分块 16 → 32，减半 I2C 事务
s = s.replace('''        unsigned char buf[17];
        for (int i = 0; i < 128; i += 16) {
            int m = (128 - i > 16) ? 16 : (128 - i);''',
              '''        unsigned char buf[33];
        for (int i = 0; i < 128; i += 32) {
            int m = (128 - i > 32) ? 32 : (128 - i);''', 1)

# 3) NFC 等待时间 30ms → 12ms（避免阻塞主循环）
s = s.replace('while ((int)(now_ms() - t0) < 30) {', 'while ((int)(now_ms() - t0) < 12) {')
s = s.replace('if (g_nfc_ok && g_lock_state == 0 && t - nfc_tick > 800) {',
              'if (g_nfc_ok && g_lock_state == 0 && t - nfc_tick > 1200) {', 1)

# 4) 键盘每轮都扫（原来 n%2）
s = s.replace('if (!g_fp_suspend && n % 2 == 0) {', 'if (!g_fp_suspend) {', 1)

s = s.replace("rk2206-lock-v47", "rk2206-lock-v48")
open(P, "w", encoding="utf-8").write(s)
print("patched v48")
