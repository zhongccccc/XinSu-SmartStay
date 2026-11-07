# -*- coding: utf-8 -*-
"""v55：开/关锁改为阻塞式驱动，保证通电时间足量。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

anchor = "static void zk_print(const char *fmt, ...)"
HELPERS = '''/* 阻塞式驱动电机：通足 ms 毫秒后刹车（与 zk gpio 测试一致） */
static void motor_drive_blocking(int dir, unsigned int ms)
{
    if (ms == 0) ms = 1;
    if (ms > 3000) ms = 3000;
    if (dir > 0) {
        IoTGpioSetOutputVal(PIN_MOTOR_IB, IOT_GPIO_VALUE0);
        IoTGpioSetOutputVal(PIN_MOTOR_IA, IOT_GPIO_VALUE1);
    } else {
        IoTGpioSetOutputVal(PIN_MOTOR_IA, IOT_GPIO_VALUE0);
        IoTGpioSetOutputVal(PIN_MOTOR_IB, IOT_GPIO_VALUE1);
    }
    usleep(ms * 1000);
    motor_brake();
    g_motor_dir = 0;
}

'''
if 'motor_drive_blocking' not in s:
    s = s.replace(anchor, HELPERS + anchor, 1)

# do_open 整体替换
start = s.index("static void do_open(const char *why)")
end = s.index("/* ================= 键盘 ================= */")
NEW = '''static void do_open(const char *why)
{
    if (g_lock_state == 1) return;
    zk_print("ZK|EVT|DOOR|open|%s\\r\\n", why);
    g_opens++;
    g_lock_state = 1;
    motor_drive_blocking(+1, g_open_ms);
    g_beep_until = now_ms() + 140;
    g_auto_lock_at = now_ms() + AUTO_LOCK_MS;
    g_oled_dirty = 1;
}

static void do_lock(const char *why)
{
    if (g_lock_state == 0) return;
    zk_print("ZK|EVT|DOOR|close|%s\\r\\n", why);
    g_lock_state = 0;
    g_auto_lock_at = 0;
    motor_drive_blocking(-1, g_lock_ms);
    g_beep_until = now_ms() + 140;
    g_oled_dirty = 1;
}

'''
s = s[:start] + NEW + s[end:]

s = s.replace("rk2206-lock-v54", "rk2206-lock-v55")
open(P, "w", encoding="utf-8").write(s)
print("patched v55 ok")
