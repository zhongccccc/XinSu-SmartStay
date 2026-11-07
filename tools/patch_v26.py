# -*- coding: utf-8 -*-
"""v26：加 zk sda —— 直接采样 SDA 电平与慢速时钟读取，判断键盘是否在输出。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

DIAG = '''/* ---------------- SDA 电平诊断 ---------------- */
static void zk_sda_diag(void)
{
    /* 1) 不clk，只观察 SDA 电平 40 次（每 100ms） */
    zk_print("ZK|SDA|LEVELS");
    for (int i = 0; i < 40; i++) {
        IotGpioValue s = IOT_GPIO_VALUE0;
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        zk_print("%d", s);
        usleep(100 * 1000);
    }
    zk_print("\\r\\n");

    /* 2) 慢速时钟读 16 位，把每一位都打出来 */
    zk_print("ZK|SDA|CLOCK");
    IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
    usleep(5000);
    for (int i = 0; i < 16; i++) {
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
        usleep(500);
        IotGpioValue s = IOT_GPIO_VALUE0;
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        zk_print("%d", s);
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
        usleep(500);
    }
    zk_print("\\r\\nZK|SDA|DONE\\r\\n");
}

'''

anchor = "/* ================= 指纹 ================= */"
assert anchor in s
s = s.replace(anchor, DIAG + anchor, 1)

old = '''    } else if (strcmp(sub, "learn") == 0) {'''
new = '''    } else if (strcmp(sub, "sda") == 0) {
        g_fp_suspend = 1;
        zk_sda_diag();
        g_fp_suspend = 0;
        zk_print("ZK|ACK|SDA|OK\\r\\n");
    } else if (strcmp(sub, "learn") == 0) {'''
assert old in s
s = s.replace(old, new, 1)

s = s.replace("rk2206-lock-v25", "rk2206-lock-v26")
open(P, "w", encoding="utf-8").write(s)
print("patched v26")
