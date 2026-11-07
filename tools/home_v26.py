# -*- coding: utf-8 -*-
"""v26：中文界面（字库已补字）+ 局部刷新（消除闪屏）。"""
import re

P = r"E:\zhikong\home_app\zh_home_v9.c"
s = open(P, encoding="utf-8").read()
s = re.sub(r'#define ZH_VER\s+"[^"]+"', '#define ZH_VER           "rk2206-home-v26"', s, count=1)

start = s.index("/* ---------------- 版式")
end = s.index("/* ---------------- shell ---------------- */")

NEW = r'''/* ---------------- 版式（黑白 · 中文 · 局部刷新） ----------------
 * 320x240
 *   y=6   温度 | 湿度         y=72  光照 | 燃气
 *   y=138 人体（满宽）          y=178 风扇 | 灯
 * 只重画数值变化的卡片，避免整屏重绘闪烁
 */
#define C_BLACK  0x0000
#define C_WHITE  0xFFFF
#define C_GRAY   0x8410

/* 上次显示的值，用于判断是否需要重画 */
static int d_temp10 = -9999, d_hum = -9999, d_lux = -9999, d_gas = -9999;
static int d_pir = -1, d_fan = -1, d_led = -1;

static void box(int x, int y, int w, int h, uint16_t color)
{
    lcd_fill(x, y, x + w - 1, y + h - 1, color);
}

/* 画一张卡片（含边框、标签、数值、单位） */
static void card(int x, int y, int w, const char *label, const char *value,
                 const char *unit)
{
    box(x, y, w, 60, C_WHITE);
    box(x + 2, y + 2, w - 4, 56, C_BLACK);
    lcd_show_chinese(x + 8, y + 6, (uint8_t *)label, C_GRAY, C_BLACK, 16, 0);
    lcd_show_string(x + 8, y + 28, (const uint8_t *)value, C_WHITE, C_BLACK, 24, 0);
    if (unit && unit[0]) {
        lcd_show_string(x + w - 30, y + 34, (const uint8_t *)unit, C_GRAY, C_BLACK, 16, 0);
    }
}

/* 人体状态条 */
static void pir_banner(int active)
{
    if (active) {
        box(8, 138, 304, 34, C_WHITE);
        lcd_show_chinese(18, 147, "人体", C_BLACK, C_WHITE, 16, 0);
        lcd_show_chinese(210, 147, "有人", C_BLACK, C_WHITE, 16, 0);
    } else {
        box(8, 138, 304, 34, C_WHITE);
        box(10, 140, 300, 30, C_BLACK);
        lcd_show_chinese(18, 147, "人体", C_WHITE, C_BLACK, 16, 0);
        lcd_show_chinese(210, 147, "无人", C_GRAY, C_BLACK, 16, 0);
    }
}

/* 半宽开关：开=白底黑字，关=黑底白字 */
static void sw(int x, int y, const char *label, int on)
{
    if (on) {
        box(x, y, 148, 40, C_WHITE);
        lcd_show_chinese(x + 12, y + 12, (uint8_t *)label, C_BLACK, C_WHITE, 16, 0);
        lcd_show_chinese(x + 104, y + 12, "开", C_BLACK, C_WHITE, 16, 0);
    } else {
        box(x, y, 148, 40, C_WHITE);
        box(x + 2, y + 2, 144, 36, C_BLACK);
        lcd_show_chinese(x + 12, y + 12, (uint8_t *)label, C_WHITE, C_BLACK, 16, 0);
        lcd_show_chinese(x + 104, y + 12, "关", C_GRAY, C_BLACK, 16, 0);
    }
}

static void draw_temp(void)
{
    char b[16];
    snprintf(b, sizeof(b), "%.1f", g_temp < -90 ? 0.0f : g_temp);
    card(8, 6, 148, "温度", b, "C");
}
static void draw_hum(void)
{
    char b[16];
    snprintf(b, sizeof(b), "%.0f", g_hum < 0 ? 0.0f : g_hum);
    card(164, 6, 148, "湿度", b, "%");
}
static void draw_lux(void)
{
    char b[16];
    snprintf(b, sizeof(b), "%d", g_lux < 0 ? 0 : g_lux);
    card(8, 72, 148, "光照", b, "lx");
}
static void draw_gas(void)
{
    char b[16];
    snprintf(b, sizeof(b), "%d", g_gas);
    card(164, 72, 148, "燃气", b, "");
}

/* 全量重画（开机 / 手动刷新） */
static void dash_full(void)
{
    char b[16];

    box(0, 0, LCD_W, LCD_H, C_BLACK);

    snprintf(b, sizeof(b), "%.1f", g_temp < -90 ? 0.0f : g_temp);
    card(8, 6, 148, "温度", b, "C");
    snprintf(b, sizeof(b), "%.0f", g_hum < 0 ? 0.0f : g_hum);
    card(164, 6, 148, "湿度", b, "%");
    snprintf(b, sizeof(b), "%d", g_lux < 0 ? 0 : g_lux);
    card(8, 72, 148, "光照", b, "lx");
    snprintf(b, sizeof(b), "%d", g_gas);
    card(164, 72, 148, "燃气", b, "");

    pir_banner(g_pir);
    sw(8, 178, "风扇", g_fan_duty > 0);
    sw(164, 178, "灯", g_led_on > 0);

    d_temp10 = (int)(g_temp * 10);
    d_hum = (int)g_hum;
    d_lux = g_lux;
    d_gas = g_gas;
    d_pir = g_pir ? 1 : 0;
    d_fan = g_fan_duty > 0 ? 1 : 0;
    d_led = g_led_on > 0 ? 1 : 0;
}

/* 增量刷新：只重画变化的那一块 */
static void dash_sync(void)
{
    int t10 = (int)(g_temp * 10);
    int h = (int)g_hum;
    int f = g_fan_duty > 0 ? 1 : 0;
    int l = g_led_on > 0 ? 1 : 0;
    int p = g_pir ? 1 : 0;

    if (t10 != d_temp10) { d_temp10 = t10; draw_temp(); }
    if (h != d_hum)      { d_hum = h;       draw_hum(); }
    if (g_lux != d_lux)  { d_lux = g_lux;   draw_lux(); }
    /* 燃气抖动较大，变化超过 8 才重画 */
    if (abs(g_gas - d_gas) > 8) { d_gas = g_gas; draw_gas(); }
    if (p != d_pir)      { d_pir = p;       pir_banner(p); }
    if (f != d_fan)      { d_fan = f;       sw(8, 178, "风扇", f); }
    if (l != d_led)      { d_led = l;       sw(164, 178, "灯", l); }
}

'''
s = s[:start] + NEW + s[end:]

# 主循环里的重绘调用改成增量刷新
s = s.replace("if (inited_lcd) { draw_values(); }", "if (inited_lcd) { dash_sync(); }")
s = s.replace("if (inited_lcd) draw_values();", "if (inited_lcd) dash_sync();")
s = s.replace("if (inited_lcd) { draw_values(); }", "if (inited_lcd) { dash_sync(); }")

open(P, "w", encoding="utf-8").write(s)
print("v26 已写入")
print("剩余 draw_values 引用:", s.count("draw_values"))
