# -*- coding: utf-8 -*-
"""v55：开/关锁改为阻塞式驱动（与 zk gpio 相同），保证通电时间足量。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

# 1) 新增阻塞驱动函数，插在 motor_brake 之后
anchor = "static void zk_print(const char *fmt, ...)"
HELPERS = '''/* 阻塞式驱动电机：通足 ms 毫秒后刹车（与 zk gpio 测试验证过的方式一致） */
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
assert anchor in s
s = s.replace(anchor, HELPERS + anchor, 1)

# 2) do_open 改为阻塞驱动
old_open = '''    zk_print("ZK|EVT|DOOR|open|%s\\r\\n", why);
    g_motor_dir = +1;
    g_motor_deadline = now_ms() + g_open_ms;
    g_beep_until = now_ms() + 140;   /* 开锁提示音 */
    g_opens++;
    g_lock_state = 1;
    g_auto_lock_at = now_ms() + AUTO_LOCK_MS;'''
new_open = '''    zk_print("ZK|EVT|DOOR|open|%s\\r\\n", why);
    g_opens++;
    g_lock_state = 1;
    motor_drive_blocking(+1, g_open_ms);
    g_beep_until = now_ms() + 140;
    g_auto_lock_at = now_ms() + AUTO_LOCK_MS;'''
assert old_open in s
s = s.replace(old_open, new_open, 1)

# 3) do_lock 改为阻塞驱动
old_lock = '''    zk_print("ZK|EVT|DOOR|close|%s\\r\\n", why);
    g_motor_dir = -1;
    g_motor_deadline = now_ms() + g_lock_ms;
    g_beep_until = now_ms() + 140;
    g_lock_state = 0;
    g_auto_lock_at = 0;'''
new_lock = '''    zk_print("ZK|EVT|DOOR|close|%s\\r\\n", why);
    g_lock_state = 0;
    g_auto_lock_at = 0;
    motor_drive_blocking(-1, g_lock_ms);
    g_beep_until = now_ms() + 140;'''
assert old_lock in s
s = s.replace(old_lock, new_lock, 1)

s = s.replace("rk2206-lock-v54", "rk2206-lock-v55")
open(P, "w", encoding="utf-8").write(s)
print("patched v55")
