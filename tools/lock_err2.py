# -*- coding: utf-8 -*-
"""门锁固件：密码错误/成功时给明确反馈（OLED 画 X / 勾 + 不同蜂鸣）。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

if "g_err_until" not in s:
    s = s.replace("static volatile unsigned int g_beep_until = 0;",
                  "static volatile unsigned int g_beep_until = 0;\n"
                  "static volatile unsigned int g_err_until = 0;\n"
                  "static volatile unsigned int g_ok_until = 0;", 1)
    print("[1] state vars added")

OLD_RENDER = '''    /* 密码：6 个槽位，已输入的画圆点（不显示真实数字） */
    for (int i = 0; i < PIN_LEN; i++) {
        int cx = 12 + i * 20;
        if (i < g_pin_len) {
            draw_dot(cx, 38, 5);
        } else {
            rect(cx - 5, 37, 10, 3, 1);      /* 未输入：短横 */
        }
    }'''

NEW_RENDER = '''    /* 密码区：错误画 X、正确画勾、否则画输入进度 */
    unsigned int _now = now_ms();
    if (g_err_until && (int)(g_err_until - _now) > 0) {
        for (int i = 0; i < 20; i++) {
            px(46 + i, 28 + i, 1);
            px(46 + i, 47 - i, 1);
            px(47 + i, 28 + i, 1);
            px(47 + i, 47 - i, 1);
        }
    } else if (g_ok_until && (int)(g_ok_until - _now) > 0) {
        for (int i = 0; i < 8; i++)   px(48 + i, 40 + i, 1);
        for (int i = 0; i < 14; i++)  px(55 + i, 47 - i, 1);
        for (int i = 0; i < 8; i++)   px(48 + i, 41 + i, 1);
        for (int i = 0; i < 14; i++)  px(55 + i, 48 - i, 1);
    } else {
        for (int i = 0; i < PIN_LEN; i++) {
            int cx = 12 + i * 20;
            if (i < g_pin_len) {
                draw_dot(cx, 38, 5);
            } else {
                rect(cx - 5, 37, 10, 3, 1);
            }
        }
    }'''

if OLD_RENDER in s:
    s = s.replace(OLD_RENDER, NEW_RENDER, 1)
    print("[2] oled render updated")
else:
    print("[2] !! render block NOT matched")

OLD_RESULT = '''                        zk_print("ZK|EVT|CODE|%s\\r\\n", ok ? "ok" : "bad");
                        if (ok) do_open("keypad");
                        g_pin_len = 0;'''
NEW_RESULT = '''                        zk_print("ZK|EVT|CODE|%s\\r\\n", ok ? "ok" : "bad");
                        if (ok) {
                            g_ok_until = now_ms() + 800;
                            g_err_until = 0;
                            do_open("keypad");
                        } else {
                            g_err_until = now_ms() + 1800;
                            g_ok_until = 0;
                            if (g_pwm_ready) {
                                IoTPwmStart(PWM_BUZZER, 50, 2700);
                                g_beep_on = 1;
                            }
                            g_beep_until = now_ms() + 400;
                            zk_print("ZK|EVT|CODEBAD\\r\\n");
                        }
                        g_pin_len = 0;'''

if OLD_RESULT in s:
    s = s.replace(OLD_RESULT, NEW_RESULT, 1)
    print("[3] verify feedback added")
else:
    print("[3] !! verify block NOT matched")

open(P, "w", encoding="utf-8").write(s)
print("[done] written")
