# -*- coding: utf-8 -*-
"""v11：人体状态独立成格并整格高亮；光照移到主指标右侧。"""
P = r"E:\zhikong\home_app\zh_home_v9.c"
s = open(P, encoding="utf-8").read()

s = s.replace('ZH_VER           "rk2206-home-v10"', 'ZH_VER           "rk2206-home-v11"')

# 1) 标题栏去掉人体（只留标题）
start = s.index("static void draw_header(void)")
end = s.index("static void hero_frame(void)")
s = s[:start] + '''static void draw_header(void)
{
    lcd_fill(0, 0, LCD_W, HEAD_H, C_HEAD);
    lcd_show_chinese(8, 4, "芯宿智控", C_WHITE, C_HEAD, 24, 0);
    lcd_show_string(210, 10, "SMART HOME", C_SUB, C_HEAD, 16, 0);
}

''' + s[end:]

# 2) hero 右侧改为 湿度 + 光照
start = s.index("static void hero_frame(void)")
end = s.index("static void footer_frame(void)")
s = s[:start] + '''static void hero_frame(void)
{
    lcd_fill(0, HERO_Y, LCD_W, HERO_Y + HERO_H, C_BG);
    lcd_show_chinese(16, HERO_Y + 8, "室内温度", C_SUB, C_BG, 16, 0);
    lcd_show_string(150, HERO_Y + 44, "C", C_CYAN, C_BG, 32, 0);

    lcd_show_chinese(216, HERO_Y + 4, "湿度", C_SUB, C_BG, 16, 0);
    lcd_show_string(292, HERO_Y + 22, "%", C_GREEN, C_BG, 16, 0);
    lcd_show_chinese(216, HERO_Y + 58, "光照", C_SUB, C_BG, 16, 0);
    lcd_show_string(292, HERO_Y + 76, "lx", C_YELLOW, C_BG, 16, 0);
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
        lcd_fill(214, HERO_Y + 18, 290, HERO_Y + 54, C_BG);
        lcd_show_float_num1(216, HERO_Y + 22, g_hum, 4, C_GREEN, C_BG, 24);
    }
    if (g_lux != d_lux) {
        d_lux = g_lux;
        lcd_fill(214, HERO_Y + 72, 290, HERO_Y + 108, C_BG);
        lcd_show_int_num(216, HERO_Y + 76, (uint16_t)(g_lux < 0 ? 0 : g_lux), 4, C_YELLOW, C_BG, 24);
    }
}

''' + s[end:]

# 3) 底部改成 人体 / 燃气 / 灯光
start = s.index("static void footer_frame(void)")
end = s.index("static void footer_sync(void)")
s = s[:start] + '''static void footer_frame(void)
{
    int y = FOOT_Y;
    lcd_fill(0, y, LCD_W, LCD_H, C_BG);
    lcd_draw_line(0, y, LCD_W, y, C_LINE);
    lcd_fill(0, y + 1, 106, LCD_H, (g_pir ? 0x5800 : 0x0841));
    lcd_draw_line(107, y + 4, 107, LCD_H, C_LINE);
    lcd_draw_line(213, y + 4, 213, LCD_H, C_LINE);

    lcd_show_chinese(12, y + 6, "人体感应", C_SUB, g_pir ? 0x5800 : 0x0841, 16, 0);
    lcd_show_chinese(119, y + 6, "燃气", C_SUB, C_BG, 16, 0);
    lcd_show_chinese(225, y + 6, "灯光", C_SUB, C_BG, 16, 0);
}

/* 只刷新某一格 */
static void footer_cell(int idx)
{
    int y = FOOT_Y;
    if (idx == 0) {
        uint16_t bg = g_pir ? 0x5800 : 0x0841;
        lcd_fill(0, y + 1, 106, LCD_H, bg);
        lcd_show_chinese(12, y + 6, "人体感应", C_SUB, bg, 16, 0);
        if (g_pir) lcd_show_chinese(12, y + 34, "有人", C_WHITE, bg, 24, 0);
        else       lcd_show_chinese(12, y + 34, "无人", C_SUB, bg, 24, 0);
    } else if (idx == 1) {
        lcd_fill(108, y + 28, 212, y + 62, C_BG);
        if (g_gas > 2500) lcd_show_chinese(119, y + 32, "报警", C_RED, C_BG, 24, 0);
        else              lcd_show_chinese(119, y + 32, "正常", C_GREEN, C_BG, 24, 0);
    } else {
        lcd_fill(214, y + 28, 318, y + 62, C_BG);
        if (g_led_on) lcd_show_chinese(225, y + 32, "已开", C_ORANGE, C_BG, 24, 0);
        else          lcd_show_chinese(225, y + 32, "已关", C_SUB, C_BG, 24, 0);
    }
}

''' + s[end:]

# 4) footer_sync 处理人体
s = s.replace('''static void footer_sync(void)
{
    int alarm = (g_gas > 2500) ? 1 : 0;
    if (g_lux != d_lux)        { d_lux = g_lux;            footer_cell(0); }
    if (alarm != d_gas_alarm)  { d_gas_alarm = alarm;      footer_cell(1); }
    if (g_led_on != d_led)     { d_led = g_led_on;         footer_cell(2); }
}''',
'''static void footer_sync(void)
{
    int alarm = (g_gas > 2500) ? 1 : 0;
    if (g_pir != d_pir)        { d_pir = g_pir;            footer_cell(0); }
    if (alarm != d_gas_alarm)  { d_gas_alarm = alarm;      footer_cell(1); }
    if (g_led_on != d_led)     { d_led = g_led_on;         footer_cell(2); }
}''', 1)

# 5) dash_full 里的重置
s = s.replace('    d_lux = -99999; d_gas_alarm = -1; d_led = -1;',
              '    d_lux = -99999; d_gas_alarm = -1; d_led = -1; d_pir = -1;', 1)

open(P, "w", encoding="utf-8").write(s)
print("patched v11")
