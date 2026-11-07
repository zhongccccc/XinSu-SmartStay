# -*- coding: utf-8 -*-
"""v19：去掉去抖，恢复 50us 时序，新增 zk raw 连续打印掩码。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

# 1) 读时序恢复 50us
old_read = '''    for (int i = 0; i < 16; i++) {
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
        usleep(200);
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
        usleep(200);
        IotGpioValue sda = IOT_GPIO_VALUE0;
        IoTGpioGetInputVal(PIN_TK_SDA, &sda);
        /* TTP229 低电平有效：读到 0 表示该键按下 */
        if (sda == IOT_GPIO_VALUE0) {
            v |= (1u << i);
        }
    }
    return v;'''
new_read = '''    for (int i = 0; i < 16; i++) {
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
        usleep(50);
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
        usleep(50);
        IotGpioValue sda = IOT_GPIO_VALUE0;
        IoTGpioGetInputVal(PIN_TK_SDA, &sda);
        /* TTP229 低电平有效：读到 0 表示该键按下 */
        if (sda == IOT_GPIO_VALUE0) {
            v |= (1u << i);
        }
        usleep(50);
    }
    return v;'''
assert old_read in s
s = s.replace(old_read, new_read, 1)

# 2) 去掉去抖，恢复简单比较
old_scan = '''        /* 键盘：每轮扫（约 20ms），连续两次相同且非零才算按下 */
        {
            unsigned int m = ttp229_read();
            if (m != 0) {
                if (m == g_last_raw) {
                    g_same_cnt++;
                } else {
                    g_same_cnt = 0;
                }
                g_last_raw = m;
            } else {
                g_same_cnt = 0;
                g_last_raw = 0;
            }
            if (m != last_mask && (m == 0 || g_same_cnt >= 1)) {'''
new_scan = '''        /* 键盘：每 100ms 扫一次，任何变化都上报（不做去抖） */
        if (n % 5 == 0) {
            unsigned int m = ttp229_read();
            if (m != last_mask) {'''
assert old_scan in s
s = s.replace(old_scan, new_scan, 1)

# 3) zk raw：连续打印 10 次掩码
old_cmd = '''    } else if (strcmp(sub, "diag") == 0) {'''
new_cmd = '''    } else if (strcmp(sub, "raw") == 0) {
        for (int i = 0; i < 10; i++) {
            zk_print("ZK|RAW|%d|0x%04X\\r\\n", i, ttp229_read());
            usleep(150 * 1000);
        }
        zk_print("ZK|ACK|RAW|OK\\r\\n");
    } else if (strcmp(sub, "diag") == 0) {'''
assert old_cmd in s
s = s.replace(old_cmd, new_cmd, 1)

s = s.replace("rk2206-lock-v18", "rk2206-lock-v19")
open(P, "w", encoding="utf-8").write(s)
print("patched v19")
