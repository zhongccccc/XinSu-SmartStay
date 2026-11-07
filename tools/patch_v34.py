# -*- coding: utf-8 -*-
"""v34：TTP229 两线协议最终版——先等 SDO 低→高脉冲，再以 ~500kHz 打 16 位。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

start = s.index("/* TTP229-BSF 官方串行时序")
end = s.index("static char mask_to_key(unsigned int m)")

NEW = '''/* TTP229 两线协议（参考 taubedonner/ttp229b-arduino）：
 *   1) 等 SDO 由高变低（触摸）
 *   2) 等 SDO 由低回高（数据就绪）
 *   3) 等 10us
 *   4) 16 次：SCL=0 → 读 SDO（低=按下）→ SCL=1，每位约 2us
 */
static void tk_udelay(void)
{
    for (volatile int i = 0; i < 120; i++) {
        __asm__ volatile("nop");
    }
}

static int tk_wait_touch(void)
{
    unsigned int t0 = now_ms();

    /* 等 SDO 低 */
    while ((int)(now_ms() - t0) < 80) {
        IotGpioValue s = IOT_GPIO_VALUE1;
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        if (s == IOT_GPIO_VALUE0) break;
        usleep(1000);
    }
    if ((int)(now_ms() - t0) >= 80) return 0;

    /* 等 SDO 回高 */
    t0 = now_ms();
    while ((int)(now_ms() - t0) < 80) {
        IotGpioValue s = IOT_GPIO_VALUE0;
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        if (s == IOT_GPIO_VALUE1) break;
        usleep(1000);
    }
    if ((int)(now_ms() - t0) >= 80) return 0;

    tk_udelay();
    return 1;
}

static unsigned int ttp229_read(void)
{
    unsigned int v = 0;

    if (!tk_wait_touch()) {
        return 0;
    }

    for (int i = 0; i < 16; i++) {
        IotGpioValue s = IOT_GPIO_VALUE1;
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
        tk_udelay();
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        if (s == IOT_GPIO_VALUE0) v |= (1u << i);
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
        tk_udelay();
    }
    return v;
}

'''
s = s[:start] + NEW + s[end:]

# 学习循环恢复连续采样（读取本身已含等待）
s = s.replace("            usleep(300 * 1000);   /* 官方示例约每秒一次，避免压垮芯片 */\n", "")
s = s.replace("rk2206-lock-v33", "rk2206-lock-v34")
open(P, "w", encoding="utf-8").write(s)
print("patched v34")
