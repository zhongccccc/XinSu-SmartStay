# -*- coding: utf-8 -*-
"""v20：按 TTP229 手册重写两线读——起始条件 + MSB 在前。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

old = s[s.index("static unsigned int ttp229_read(void)"):s.index("/* 把 16 位映射成按键字符")]
new = '''static unsigned int ttp229_read(void)
{
    unsigned int v = 0;

    /* ---- 起始条件：SCL=1 时 SDO 由高变低 ---- */
    IoTGpioSetDir(PIN_TK_SDA, IOT_GPIO_DIR_OUT);
    IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
    IoTGpioSetOutputVal(PIN_TK_SDA, IOT_GPIO_VALUE1);
    usleep(100);
    IoTGpioSetOutputVal(PIN_TK_SDA, IOT_GPIO_VALUE0);
    usleep(100);
    IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
    usleep(100);

    /* 释放 SDO，后续由芯片驱动 */
    IoTGpioSetDir(PIN_TK_SDA, IOT_GPIO_DIR_IN);
    usleep(50);

    /* ---- 读 16 位，MSB 在前，SCL 上升沿后取值 ---- */
    for (int i = 0; i < 16; i++) {
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
        usleep(100);
        IotGpioValue sda = IOT_GPIO_VALUE0;
        IoTGpioGetInputVal(PIN_TK_SDA, &sda);
        v <<= 1;
        if (sda == IOT_GPIO_VALUE0) {
            v |= 1;                 /* 低电平有效 */
        }
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
        usleep(100);
    }
    return v;
}

'''
s = s.replace(old, new, 1)

# 位号提取也要反一下（MSB 在前，bit0 对应第 16 位）
old_bit = '''                    int bit = -1;
                    for (int bi = 0; bi < 16; bi++) {
                        if (m & (1u << bi)) { bit = bi; break; }
                    }'''
new_bit = '''                    int bit = -1;
                    /* m 是 MSB 在前拼出来的，bit0 代表第 16 个键 */
                    for (int bi = 15; bi >= 0; bi--) {
                        if (m & (1u << bi)) { bit = 15 - bi; break; }
                    }'''
assert old_bit in s
s = s.replace(old_bit, new_bit, 1)

s = s.replace("rk2206-lock-v19", "rk2206-lock-v20")
open(P, "w", encoding="utf-8").write(s)
print("patched v20")
