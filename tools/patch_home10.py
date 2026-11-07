# -*- coding: utf-8 -*-
"""v10：底部只在数值变化时局部刷新，消除闪烁。"""
P = r"E:\zhikong\home_app\zh_home_v9.c"
s = open(P, encoding="utf-8").read()

s = s.replace('ZH_VER           "rk2206-home-v9"', 'ZH_VER           "rk2206-home-v10"')

# 1) 记录上次绘制的值
s = s.replace('static int g_lux = -1, g_gas = 0, g_pir = 0, g_led_on = 0, g_auto = 1;',
'''static int g_lux = -1, g_gas = 0, g_pir = 0, g_led_on = 0, g_auto = 1;

/* 上次绘制值，用于"只在变化时刷新" */
static int d_lux = -99999, d_gas_alarm = -1, d_led = -1, d_pir = -1;
static float d_temp = -999.0f, d_hum = -999.0f;''', 1)

# 2) 底部改成"单格刷新"
old_footer = s[s.index("static void draw_footer(void)"):s.index("static void dash_full(void)")]
new_footer = '''static void footer_frame(void)
{
    int y = FOOT_Y;
    lcd_fill(0, y, LCD_W, LCD_H, C_BG);
    lcd_draw_line(0, y, LCD_W, y, C_LINE);
    lcd_draw_line(107, y + 4, 107, LCD_H, C_LINE);
    lcd_draw_line(213, y + 4, 213, LCD_H, C_LINE);

    lcd_show_chinese(12, y + 8, "光照", C_SUB, C_BG, 16, 0);
    lcd_show_chinese(119, y + 8, "燃气", C_SUB, C_BG, 16, 0);
    lcd_show_chinese(225, y + 8, "灯光", C_SUB, C_BG, 16, 0);
}

/* 只刷新某一格的值，避免整块重画导致闪烁 */
static void footer_cell(int idx)
{
    int y = FOOT_Y;
    if (idx == 0) {
        lcd_fill(6, y + 28, 104, y + 60, C_BG);
        lcd_show_int_num(12, y + 32, (uint16_t)(g_lux < 0 ? 0 : g_lux), 4, C_YELLOW, C_BG, 24);
    } else if (idx == 1) {
        lcd_fill(112, y + 28, 210, y + 60, C_BG);
        if (g_gas > 2500) lcd_show_chinese(119, y + 32, "报警", C_RED, C_BG, 24, 0);
        else              lcd_show_chinese(119, y + 32, "正常", C_GREEN, C_BG, 24, 0);
    } else {
        lcd_fill(218, y + 28, 316, y + 60, C_BG);
        if (g_led_on) lcd_show_chinese(225, y + 32, "已开", C_ORANGE, C_BG, 24, 0);
        else          lcd_show_chinese(225, y + 32, "已关", C_SUB, C_BG, 24, 0);
    }
}

static void footer_sync(void)
{
    int alarm = (g_gas > 2500) ? 1 : 0;
    if (g_lux != d_lux)        { d_lux = g_lux;            footer_cell(0); }
    if (alarm != d_gas_alarm)  { d_gas_alarm = alarm;      footer_cell(1); }
    if (g_led_on != d_led)     { d_led = g_led_on;         footer_cell(2); }
}

'''
s = s.replace(old_footer, new_footer, 1)

# 3) hero 只在变化时刷新
old_hero = s[s.index("static void draw_hero(void)"):s.index("static void footer_frame(void)")]
new_hero = '''static void hero_frame(void)
{
    lcd_fill(0, HERO_Y, LCD_W, HERO_Y + HERO_H, C_BG);
    lcd_show_chinese(16, HERO_Y + 8, "室内温度", C_SUB, C_BG, 16, 0);
    lcd_show_string(150, HERO_Y + 44, "C", C_CYAN, C_BG, 32, 0);
    lcd_show_chinese(216, HERO_Y + 12, "湿度", C_SUB, C_BG, 16, 0);
    lcd_show_string(292, HERO_Y + 46, "%", C_GREEN, C_BG, 16, 0);
}

static void hero_sync(void)
{
    float dt = g_temp - d_temp;
    float dh = g_hum - d_hum;
    if (dt > 0.09f || dt < -0.09f) {
        d_temp = g_temp;
        lcd_fill(14, HERO_Y + 30, 146, HERO_Y + 78, C_BG);
        lcd_show_float_num1(16, HERO_Y + 34, g_temp, 4, C_CYAN, C_BG, 32);
    }
    if (dh > 0.09f || dh < -0.09f) {
        d_hum = g_hum;
        lcd_fill(214, HERO_Y + 36, 290, HERO_Y + 76, C_BG);
        lcd_show_float_num1(216, HERO_Y + 40, g_hum, 4, C_GREEN, C_BG, 24);
    }
}

'''
s = s.replace(old_hero, new_hero, 1)

# 4) dash_full 与主循环改用新函数
s = s.replace('''static void dash_full(void)
{
    lcd_fill(0, 0, LCD_W, LCD_H, C_BG);
    draw_header();
    draw_hero();
    draw_footer();
}''',
'''static void dash_full(void)
{
    lcd_fill(0, 0, LCD_W, LCD_H, C_BG);
    draw_header();
    hero_frame();
    footer_frame();
    d_temp = -999.0f; d_hum = -999.0f;
    d_lux = -99999; d_gas_alarm = -1; d_led = -1;
    hero_sync();
    footer_sync();
}''', 1)

s = s.replace('if (inited_lcd) { draw_hero(); draw_footer(); }', 'if (inited_lcd) { hero_sync(); footer_sync(); }')
s = s.replace('if (inited_lcd) { draw_header(); draw_footer(); }', 'if (inited_lcd) { draw_header(); footer_sync(); }')
s = s.replace('if (inited_lcd) draw_footer();\n        zh_print("ZH|ACK|RGB|OK', 'if (inited_lcd) footer_sync();\n        zh_print("ZH|ACK|RGB|OK')
s = s.replace('if (inited_lcd) draw_footer();\n        zh_print("ZH|ACK|RGB|OFF', 'if (inited_lcd) footer_sync();\n        zh_print("ZH|ACK|RGB|OFF')

open(P, "w", encoding="utf-8").write(s)
print("patched v10")
