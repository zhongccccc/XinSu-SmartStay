# -*- coding: utf-8 -*-
"""v16：键盘快速扫描 + 去抖；新增 zk led 直测。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

# 1) 读键时序：200us/位，约 10ms 一扫（比原 50us 更稳，比 500us 更快）
old_read = '''    for (int i = 0; i < 16; i++) {
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
new_read = '''    for (int i = 0; i < 16; i++) {
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
assert old_read in s, "读键时序片段未找到"
s = s.replace(old_read, new_read, 1)

# 2) 主循环：每轮都扫（20ms），带去抖
old_scan = '''        /* 键盘：每 120ms 扫一次 */
        if (n % 6 == 0) {
            unsigned int m = ttp229_read();
            if (m != last_mask) {
                last_mask = m;
                if (m == 0) {
                    led_off();
                }
                char k = ttp229_key(m);
                if (k) {'''
new_scan = '''        /* 键盘：每轮扫（约 20ms），连续两次相同且非零才算按下 */
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
            if (m != last_mask && (m == 0 || g_same_cnt >= 1)) {
                last_mask = m;
                if (m == 0) {
                    led_off();
                }
                char k = ttp229_key(m);
                if (k) {'''
assert old_scan in s, "主循环扫描片段未找到"
s = s.replace(old_scan, new_scan, 1)

# 3) 全局变量
old_vars = '''static char g_pin[PIN_LEN + 1];'''
new_vars = '''static unsigned int g_last_raw = 0;
static int g_same_cnt = 0;
static char g_pin[PIN_LEN + 1];'''
assert old_vars in s
s = s.replace(old_vars, new_vars, 1)

# 4) zk led 直测
old_cmd = '''    } else if (strcmp(sub, "keytest") == 0) {'''
new_cmd = '''    } else if (strcmp(sub, "led") == 0) {
        unsigned int mask = (argc > 2) ? (unsigned int)strtoul(argv[2], NULL, 0) : 0xFFF;
        led_show(mask);
        zk_print("ZK|ACK|LED|OK|0x%04X\\r\\n", mask);
    } else if (strcmp(sub, "ledoff") == 0) {
        led_off();
        zk_print("ZK|ACK|LEDOFF|OK\\r\\n");
    } else if (strcmp(sub, "keytest") == 0) {'''
assert old_cmd in s
s = s.replace(old_cmd, new_cmd, 1)

s = s.replace("rk2206-lock-v15", "rk2206-lock-v16")
open(P, "w", encoding="utf-8").write(s)
print("patched v16")
