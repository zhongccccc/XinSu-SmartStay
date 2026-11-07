# -*- coding: utf-8 -*-
"""v12：感应灯延时熄灭（有人亮、无人 30 秒后自动关）。"""
P = r"E:\zhikong\home_app\zh_home_v9.c"
s = open(P, encoding="utf-8").read()

s = s.replace('ZH_VER           "rk2206-home-v11"', 'ZH_VER           "rk2206-home-v12"')

# 1) 加延时常量与状态
s = s.replace('static int g_lux = -1, g_gas = 0, g_pir = 0, g_led_on = 0, g_auto = 1;',
'''static int g_lux = -1, g_gas = 0, g_pir = 0, g_led_on = 0, g_auto = 1;
static unsigned int g_light_until = 0;   /* 到这个时刻自动关灯 */
#define LIGHT_KEEP_MS  30000             /* 无人后 30 秒关灯 */

static unsigned int zh_now_ms(void)
{
    uint32_t tick = osKernelGetTickCount();
    uint32_t freq = osKernelGetTickFreq();
    return freq ? (unsigned int)((uint64_t)tick * 1000u / freq) : tick;
}''', 1)

# 2) 主循环：有人时续期，超时关灯
s = s.replace('''            zh_print("ZH|EVT|PIR|%d\\r\\n", p);
            if (p && g_auto) rgb_set(100, 80, 40);
            if (inited_lcd) { draw_header(); footer_sync(); }''',
'''            zh_print("ZH|EVT|PIR|%d\\r\\n", p);
            if (p && g_auto) {
                rgb_set(100, 80, 40);
                g_light_until = zh_now_ms() + LIGHT_KEEP_MS;
            }
            if (inited_lcd) { footer_sync(); }''', 1)

# 3) 循环里加"超时关灯"
s = s.replace('''        if (n % 8 == 0) {
            sht30_read();''',
'''        /* 无人一段时间后自动关灯 */
        if (g_led_on && g_light_until && (int)(g_light_until - zh_now_ms()) <= 0) {
            rgb_set(0, 0, 0);
            g_light_until = 0;
            zh_print("ZH|EVT|LIGHT|off\\r\\n");
            if (inited_lcd) footer_sync();
        }

        if (n % 8 == 0) {
            sht30_read();''', 1)

# 4) 手动灯控命令
s = s.replace('''    } else if (strcmp(sub, "auto") == 0) {''',
'''    } else if (strcmp(sub, "light") == 0) {
        if (argc > 2 && strcmp(argv[2], "on") == 0) {
            rgb_set(100, 80, 40);
            g_light_until = zh_now_ms() + LIGHT_KEEP_MS;
        } else {
            rgb_set(0, 0, 0);
            g_light_until = 0;
        }
        if (inited_lcd) footer_sync();
        zh_print("ZH|ACK|LIGHT|%d\\r\\n", g_led_on);
    } else if (strcmp(sub, "auto") == 0) {''', 1)

open(P, "w", encoding="utf-8").write(s)
print("patched v12")
