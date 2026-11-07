# -*- coding: utf-8 -*-
"""v25：黑白界面 + 完整 5 项指标（温度/湿度/光照/燃气/人体）+ 风扇/灯开关。
字库只有"温度 湿度 开"等少量汉字，其余用英文标签避免乱码。"""
import re

P = r"E:\zhikong\home_app\zh_home_v9.c"
s = open(P, encoding="utf-8").read()
s = re.sub(r'#define ZH_VER\s+"[^"]+"', '#define ZH_VER           "rk2206-home-v25"', s, count=1)

start = s.index("/* ---------------- 版式")
end = s.index("/* ---------------- shell ---------------- */")

NEW = r'''/* ---------------- 版式（黑白 · 5 指标） ----------------
 * 320x240：
 *   y=6   温度(148x60) | 湿度(148x60)
 *   y=72  光照(148x60) | 燃气(148x60)
 *   y=138 人体(304x34)
 *   y=178 风扇(148x40) | 灯(148x40)
 * 字库只有少量汉字，除"温度/湿度"外一律用英文，避免乱码。
 */
#define C_BLACK  0x0000
#define C_WHITE  0xFFFF
#define C_GRAY   0x8410
#define C_DARK   0x2104

static void box(int x, int y, int w, int h, uint16_t color)
{
    lcd_fill(x, y, x + w - 1, y + h - 1, color);
}

/* 小卡片：白底黑字（更醒目） */
static void card5(int x, int y, int w, const char *label, const char *value,
                  const char *unit)
{
    box(x, y, w, 60, C_WHITE);
    box(x + 2, y + 2, w - 4, 56, C_BLACK);
    lcd_show_string(x + 8, y + 6, (const uint8_t *)label, C_GRAY, C_BLACK, 16, 0);
    lcd_show_string(x + 8, y + 28, (const uint8_t *)value, C_WHITE, C_BLACK, 24, 0);
    if (unit && unit[0]) {
        lcd_show_string(x + w - 34, y + 34, (const uint8_t *)unit, C_GRAY, C_BLACK, 16, 0);
    }
}

/* 满宽状态条 */
static void banner(int y, const char *label, const char *value, int active)
{
    if (active) {
        box(8, y, 304, 34, C_WHITE);
        lcd_show_string(18, y + 9, (const uint8_t *)label, C_BLACK, C_WHITE, 16, 0);
        lcd_show_string(200, y + 9, (const uint8_t *)value, C_BLACK, C_WHITE, 16, 0);
    } else {
        box(8, y, 304, 34, C_WHITE);
        box(10, y + 2, 300, 30, C_BLACK);
        lcd_show_string(18, y + 9, (const uint8_t *)label, C_WHITE, C_BLACK, 16, 0);
        lcd_show_string(200, y + 9, (const uint8_t *)value, C_GRAY, C_BLACK, 16, 0);
    }
}

/* 半宽开关 */
static void switch_half(int x, int y, const char *label, int on)
{
    if (on) {
        box(x, y, 148, 40, C_WHITE);
        lcd_show_string(x + 12, y + 12, (const uint8_t *)label, C_BLACK, C_WHITE, 16, 0);
        lcd_show_string(x + 112, y + 12, "ON", C_BLACK, C_WHITE, 16, 0);
    } else {
        box(x, y, 148, 40, C_WHITE);
        box(x + 2, y + 2, 144, 36, C_BLACK);
        lcd_show_string(x + 12, y + 12, (const uint8_t *)label, C_WHITE, C_BLACK, 16, 0);
        lcd_show_string(x + 112, y + 12, "OFF", C_GRAY, C_BLACK, 16, 0);
    }
}

static void draw_values(void)
{
    char buf[16];

    box(0, 0, LCD_W, LCD_H, C_BLACK);

    /* 温度（汉字可用） */
    snprintf(buf, sizeof(buf), "%.1f", g_temp < -90 ? 0.0f : g_temp);
    box(8, 6, 148, 60, C_WHITE);
    box(10, 8, 144, 56, C_BLACK);
    lcd_show_chinese(18, 12, "温度", C_GRAY, C_BLACK, 16, 0);
    lcd_show_string(18, 34, (const uint8_t *)buf, C_WHITE, C_BLACK, 24, 0);
    lcd_show_string(122, 40, "C", C_GRAY, C_BLACK, 16, 0);

    /* 湿度（汉字可用） */
    snprintf(buf, sizeof(buf), "%.0f", g_hum < 0 ? 0.0f : g_hum);
    box(164, 6, 148, 60, C_WHITE);
    box(166, 8, 144, 56, C_BLACK);
    lcd_show_chinese(174, 12, "湿度", C_GRAY, C_BLACK, 16, 0);
    lcd_show_string(174, 34, (const uint8_t *)buf, C_WHITE, C_BLACK, 24, 0);
    lcd_show_string(278, 40, "%", C_GRAY, C_BLACK, 16, 0);

    /* 光照（英文标签） */
    snprintf(buf, sizeof(buf), "%d", g_lux < 0 ? 0 : g_lux);
    card5(8, 72, 148, "LIGHT", buf, "lx");

    /* 燃气 */
    snprintf(buf, sizeof(buf), "%d", g_gas);
    card5(164, 72, 148, "GAS", buf, "");

    /* 人体状态条 */
    snprintf(buf, sizeof(buf), "%s", g_pir ? "YES" : "NO");
    banner(138, "PIR  MOTION", buf, g_pir);

    /* 风扇 / 灯 */
    switch_half(8, 178, "FAN", g_fan_duty > 0);
    switch_half(164, 178, "LIGHT", g_led_on > 0);
}

static void dash_full(void)
{
    box(0, 0, LCD_W, LCD_H, C_BLACK);
    draw_values();
}

'''
s = s[:start] + NEW + s[end:]
open(P, "w", encoding="utf-8").write(s)
print("v25 已写入")
