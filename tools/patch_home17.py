# -*- coding: utf-8 -*-
"""v17：板载 4 个按键控制灯/风扇（ADC 通道 7 分压）。"""
P = r"E:\zhikong\home_app\zh_home_v9.c"
s = open(P, encoding="utf-8").read()

s = s.replace('ZH_VER           "rk2206-home-v16"', 'ZH_VER           "rk2206-home-v17"')

# 1) 按键阈值常量
s = s.replace('#define ADC_GAS          4',
'''#define ADC_GAS          4
#define ADC_KEY          7

/* 按键电压（厂商手册）：不按 3.3V / K3 0.01V / K4 1.0V / K5 1.65V / K6 0.55V
 * ADC 10bit，raw = V * 1024 / 3.3 */
#define KEY_NONE_RAW     1000
#define KEY_K3_RAW       3
#define KEY_K4_RAW       310
#define KEY_K5_RAW       512
#define KEY_K6_RAW       171
#define KEY_TOL          60''', 1)

# 2) 按键状态 + 处理函数
s = s.replace('/* 风扇：duty 1~99，0 = 停 */',
'''/* 读按键：返回 '3' '4' '5' '6' 或 0 */
static char key_read(void)
{
    unsigned short v = 0;
    if (IoTAdcGetVal(ADC_KEY, &v) != IOT_SUCCESS) return 0;
    int raw = (int)v;
    if (raw > KEY_NONE_RAW) return 0;
    if (raw < KEY_K3_RAW + KEY_TOL) return '3';
    if (raw > KEY_K6_RAW - KEY_TOL && raw < KEY_K6_RAW + KEY_TOL) return '6';
    if (raw > KEY_K4_RAW - KEY_TOL && raw < KEY_K4_RAW + KEY_TOL) return '4';
    if (raw > KEY_K5_RAW - KEY_TOL && raw < KEY_K5_RAW + KEY_TOL) return '5';
    return 0;
}

/* 风扇：duty 1~99，0 = 停 */''', 1)

# 3) 主循环里处理按键
s = s.replace('''        /* 无人一段时间后自动关灯 */''',
'''        /* 板载按键 */
        {
            char k = key_read();
            if (k != last_key) {
                last_key = k;
                if (k) {
                    zh_print("ZH|EVT|KEY|%c\\r\\n", k);
                    ensure_pwm();
                    if (k == '6') {                    /* K6：开关灯 */
                        if (g_led_on) { rgb_set(0, 0, 0); g_light_until = 0; }
                        else { rgb_set(99, 99, 99); g_light_until = zh_now_ms() + LIGHT_KEEP_MS; }
                        if (inited_lcd) footer_sync();
                    } else if (k == '4') {             /* K4：开关风扇 */
                        fan_set(g_fan_duty ? 0 : 60);
                        if (inited_lcd) footer_sync();
                    } else if (k == '5') {             /* K5：风扇调速 */
                        if (g_fan_duty == 0) fan_set(30);
                        else if (g_fan_duty < 60) fan_set(60);
                        else if (g_fan_duty < 99) fan_set(99);
                        else fan_set(0);
                        if (inited_lcd) footer_sync();
                    } else if (k == '3') {             /* K3：一键全关 */
                        rgb_set(0, 0, 0);
                        g_light_until = 0;
                        fan_set(0);
                        if (inited_lcd) footer_sync();
                    }
                }
            }
        }

        /* 无人一段时间后自动关灯 */''', 1)

# 4) last_key 变量
s = s.replace('    int last_pir = -1;', '    int last_pir = -1;\n    char last_key = 0;', 1)

# 5) 底部灯光格显示风扇
s = s.replace('''    } else {
        lcd_fill(214, y + 28, 318, y + 62, C_BG);
        if (g_led_on) lcd_show_chinese(225, y + 32, "已开", C_ORANGE, C_BG, 24, 0);
        else          lcd_show_chinese(225, y + 32, "已关", C_SUB, C_BG, 24, 0);
    }''',
'''    } else {
        lcd_fill(214, y + 28, 318, y + 62, C_BG);
        if (g_led_on) lcd_show_chinese(225, y + 32, "已开", C_ORANGE, C_BG, 24, 0);
        else          lcd_show_chinese(225, y + 32, "已关", C_SUB, C_BG, 24, 0);
    }''', 1)

# 6) 开机初始化按键 ADC
s = s.replace('''    ensure_pwm();
    rgb_set(0, 0, 0);
    fan_set(0);''',
'''    ensure_pwm();
    rgb_set(0, 0, 0);
    fan_set(0);
    IoTAdcInit(ADC_KEY);''', 1)

open(P, "w", encoding="utf-8").write(s)
print("patched v17")
