# -*- coding: utf-8 -*-
"""v35：严格按 TTP229-AQG 手册 Figure 3-4-1 时序实现。
   DV=93us  SDO 低脉冲 → 回高 → Tw=10us → 16 位时钟(约 100kHz) → T_resp=32ms
"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

start = s.index("/* TTP229 两线协议（参考 taubedonner/ttp229b-arduino）：")
end = s.index("static char mask_to_key(unsigned int m)")

NEW = '''/* TTP229-AQG 2-wire 时序（手册 Figure 3-4-1 / Table）：
 *   触摸后 SDO 拉低 DV=93us（数据有效脉冲）→ SDO 回高
 *   Tw=10us 后开始打 16 个时钟（F_SCL 1k~512kHz，这里约 100kHz）
 *   每位：SCL 低 → 读 SDO → SCL 高
 *   一帧结束必须等 T_resp=32ms 才能再读（16 键）
 */
static void tk_delay_us(unsigned int us)
{
    volatile unsigned int n = us * 18;      /* 约 1us/18 次空转 */
    while (n--) {
        __asm__ volatile("nop");
    }
}

/* 返回原始 16 位（bit=1 表示该位 SDO 为高） */
static unsigned int ttp229_read_raw(void)
{
    unsigned int v = 0;
    unsigned int guard;

    /* 1) 等 SDO 出现低脉冲（DV） */
    guard = 0;
    while (guard < 300000u) {
        IotGpioValue s = IOT_GPIO_VALUE1;
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        if (s == IOT_GPIO_VALUE0) break;
        guard++;
    }
    if (guard >= 300000u) {
        return 0;                       /* 没有触摸 */
    }

    /* 2) 等 DV 脉冲结束（SDO 回高） */
    guard = 0;
    while (guard < 300000u) {
        IotGpioValue s = IOT_GPIO_VALUE0;
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        if (s == IOT_GPIO_VALUE1) break;
        guard++;
    }

    /* 3) Tw = 10us */
    tk_delay_us(10);

    /* 4) 16 个时钟，约 100kHz（半周期 5us） */
    for (int i = 0; i < 16; i++) {
        IotGpioValue s = IOT_GPIO_VALUE0;
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
        tk_delay_us(5);
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        if (s == IOT_GPIO_VALUE1) v |= (1u << i);
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
        tk_delay_us(5);
    }

    /* 5) T_resp = 32ms */
    usleep(32 * 1000);
    return v;
}

/* 兼容旧接口：返回"按下"的位（自动判断高有效/低有效） */
static unsigned int ttp229_read(void)
{
    unsigned int raw = ttp229_read_raw();
    unsigned int hi = raw & 0xFFFFu;
    unsigned int lo = (~raw) & 0xFFFFu;

    int nhi = 0, nlo = 0;
    for (int i = 0; i < 16; i++) {
        if (hi & (1u << i)) nhi++;
        if (lo & (1u << i)) nlo++;
    }
    /* 恰好一位为"按下"的那种极性更可信 */
    if (nhi == 1) return hi;
    if (nlo == 1) return lo;
    if (nhi > 0 && nhi <= 2) return hi;
    if (nlo > 0 && nlo <= 2) return lo;
    return 0;
}

'''
s = s[:start] + NEW + s[end:]

# 学习循环：读取本身已含 32ms 间隔，去掉额外延时
s = s.replace("            if (!m) m = ttp229_read_edge();\n", "")
s = s.replace("            usleep(300 * 1000);   /* 官方示例约每秒一次，避免压垮芯片 */\n", "")
s = s.replace("rk2206-lock-v34", "rk2206-lock-v35")
open(P, "w", encoding="utf-8").write(s)
print("patched v35")
