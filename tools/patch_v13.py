# -*- coding: utf-8 -*-
"""v13：把 keytest 改成慢速连续采样，便于观察按住时的稳定值。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

old = '''static void keytest(void)
{
    for (int round = 0; round < 6; round++) {
        unsigned int a = ttp_read_A();
        unsigned int b = ttp_read_B();
        unsigned int c = ttp_read_C();
        zk_print("ZK|KEYTEST|%d|A=0x%04X|B=0x%04X|C=0x%04X\\r\\n", round, a, b, c);
        usleep(120 * 1000);
    }
}'''

new = '''static void keytest(void)
{
    /* 慢速连续采样：按住键时观察原始值是否稳定 */
    for (int round = 0; round < 10; round++) {
        unsigned int a = ttp_read_A();
        zk_print("ZK|KEYTEST|%d|0x%04X\\r\\n", round, a);
        usleep(200 * 1000);
    }
}'''
assert old in s, "keytest 块未找到"
s = s.replace(old, new, 1)

# A 时序放慢到 500us/bit，总共约 16ms 一次
old_a = '''    for (int i = 0; i < 16; i++) {
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
        usleep(60);
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
        usleep(60);
        IotGpioValue s = IOT_GPIO_VALUE0;
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        if (s == IOT_GPIO_VALUE0) v |= (1u << i);
        usleep(60);
    }
    return v;
}

static unsigned int ttp_read_B(void)'''
new_a = '''    for (int i = 0; i < 16; i++) {
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
        usleep(500);
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
        usleep(500);
        IotGpioValue s = IOT_GPIO_VALUE0;
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        if (s == IOT_GPIO_VALUE0) v |= (1u << i);
        usleep(500);
    }
    return v;
}

static unsigned int ttp_read_B(void)'''
assert old_a in s, "A 时序未找到"
s = s.replace(old_a, new_a, 1)

s = s.replace("rk2206-lock-v12", "rk2206-lock-v13")
open(P, "w", encoding="utf-8").write(s)
print("patched v13")
