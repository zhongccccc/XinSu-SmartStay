# -*- coding: utf-8 -*-
"""v32：按 TTP229-BSF 官方串行时序重写读取（SCL 高起始 → 低电平期间读 SDO，1ms 级延时）。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

start = s.index("static unsigned int ttp229_read(void)")
end = s.index("/* 降沿读法（变体 B）")
NEW = '''/* TTP229-BSF 官方串行时序（参考 micropython 驱动）：
 *   SCL=1 等 1ms 起始；重复 16 次：SCL=0 等 1ms → 读 SDO → SCL=1 等 1ms；最后等 1ms
 *   SDO 为 0 表示该键按下 */
static unsigned int ttp229_read(void)
{
    unsigned int v = 0;

    IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
    usleep(1000);

    for (int i = 0; i < 16; i++) {
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
        usleep(1000);
        IotGpioValue s = IOT_GPIO_VALUE1;
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        if (s == IOT_GPIO_VALUE0) v |= (1u << i);
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
        usleep(1000);
    }
    usleep(1000);
    return v;
}

'''
s = s[:start] + NEW + s[end:]

# 学习循环不再需要降沿兜底（官方时序已覆盖）
s = s.replace("            if (!m) m = ttp229_read_edge();\n", "")

s = s.replace("rk2206-lock-v31", "rk2206-lock-v32")
open(P, "w", encoding="utf-8").write(s)
print("patched v32")
