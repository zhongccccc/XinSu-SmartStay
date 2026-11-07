# -*- coding: utf-8 -*-
"""v25：修 TTP229 读取后 SCL 未拉低（芯片卡在半传输）的 bug。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

old = '''static unsigned int ttp229_read(void)
{
    unsigned int v = 0;
    for (int i = 0; i < 16; i++) {
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
}'''

new = '''static unsigned int ttp229_read(void)
{
    unsigned int v = 0;

    /* 起始：SCL 空闲低 */
    IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
    usleep(200);

    for (int i = 0; i < 16; i++) {
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
        usleep(80);
        IotGpioValue s = IOT_GPIO_VALUE0;
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        if (s == IOT_GPIO_VALUE0) v |= (1u << i);
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
        usleep(80);
    }

    /* 关键：读完必须把 SCL 留在低电平，否则芯片卡在半传输 */
    IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
    usleep(3000);          /* 给芯片复位内部状态的时间 */
    return v;
}'''
assert old in s, "ttp229_read 未找到"
s = s.replace(old, new, 1)

s = s.replace("rk2206-lock-v24", "rk2206-lock-v25")
open(P, "w", encoding="utf-8").write(s)
print("patched v25")
