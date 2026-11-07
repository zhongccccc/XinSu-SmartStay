# -*- coding: utf-8 -*-
"""v24：只用黑白的极简界面（不依赖颜色是否正确）。"""
P = r"E:\zhikong\home_app\zh_home_v9.c"
s = open(P, encoding="utf-8").read()

import re
s = re.sub(r'#define ZH_VER\s+"[^"]+"', '#define ZH_VER           "rk2206-home-v24"', s, count=1)

start = s.index("/* ---------------- 版式 ----------------")
end = s.index("/* ---------------- shell ---------------- */")

NEW = r'''/* ---------------- 版式（黑白极简） ----------------
 * 只用黑 / 白 / 深灰三色，避免这块屏的色偏问题：
 * 不论屏幕是否反色，都只是黑白互换，观感是一致的。
 */
#define C_BLACK  0x0000
#define C_WHITE  0xFFFF
#define C_GRAY   0x8410

static void fill_circle(int cx, int cy, int r, uint16_t color)
{
    int dy;
    for (dy = -r; dy <= r; dy++) {
        int dx = r;
        while (dx > 0 && (dx * dx + dy * dy) > (r * r)) dx--;
        if (dx > 0) lcd_fill(cx - dx, cy + dy, cx + dx, cy + dy, color);
    }
}

static void box(int x, int y, int w, int h, uint16_t color)
{
    lcd_fill(x, y, x + w - 1, y + h - 1, color);
}

/* 数值卡片：白框 + 黑底 + 白字 */
static void card(int x, int y, const char *label, const char *value, const char *unit)
{
    box(x, y, 148, 62, C_WHITE);              /* 外框 */
    box(x + 2, y + 2, 144, 58, C_BLACK);      /* 内底 */
    lcd_show_chinese(x + 10, y + 8, (uint8_t *)label, C_GRAY, C_BLACK, 16, 0);
    lcd_show_string(x + 10, y + 28, (const uint8_t *)value, C_WHITE, C_BLACK, 24, 0);
    if (unit && unit[0]) {
        lcd_show_string(x + 104, y + 36, (const uint8_t *)unit, C_GRAY, C_BLACK, 16, 0);
    }
}

/* 开关行：开=白底黑字，关=黑底白字 */
static void row(int y, const char *label, int on)
{
    if (on) {
        box(8, y, 304, 40, C_WHITE);
        lcd_show_chinese(20, y + 11, (uint8_t *)label, C_BLACK, C_WHITE, 16, 0);
        lcd_show_chinese(210, y + 11, "开", C_BLACK, C_WHITE, 16, 0);
    } else {
        box(8, y, 304, 40, C_WHITE);
        box(10, y + 2, 300, 36, C_BLACK);
        lcd_show_chinese(20, y + 11, (uint8_t *)label, C_WHITE, C_BLACK, 16, 0);
        lcd_show_chinese(210, y + 11, "关", C_GRAY, C_BLACK, 16, 0);
    }
}

static void draw_values(void)
{
    char buf[16];

    box(0, 0, LCD_W, LCD_H, C_BLACK);

    snprintf(buf, sizeof(buf), "%.1f", g_temp < -90 ? 0.0f : g_temp);
    card(8, 8, "温度", buf, "C");

    snprintf(buf, sizeof(buf), "%.0f", g_hum < 0 ? 0.0f : g_hum);
    card(164, 8, "湿度", buf, "%");

    snprintf(buf, sizeof(buf), "%d", g_lux < 0 ? 0 : g_lux);
    card(8, 76, "光照", buf, "lx");

    card(164, 76, "人体", g_pir ? "有人" : "无人", "");

    row(146, "风扇", g_fan_duty > 0);
    row(192, "灯",   g_led_on > 0);
}

static void dash_full(void)
{
    box(0, 0, LCD_W, LCD_H, C_BLACK);
    draw_values();
}

'''
s = s[:start] + NEW + s[end:]
open(P, "w", encoding="utf-8").write(s)
print("v24 黑白版已写入")
