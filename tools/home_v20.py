# -*- coding: utf-8 -*-
"""v20：按用户提供的参考图重做 LCD —— 2x2 卡片 + 风扇/灯开关行。"""
P = r"E:\zhikong\home_app\zh_home_v9.c"
s = open(P, encoding="utf-8").read()

s = s.replace('ZH_VER           "rk2206-home-v19"', 'ZH_VER           "rk2206-home-v20"')

start = s.index("/* ---------------- 版式 ---------------- */")
end = s.index("/* ---------------- shell ---------------- */")

NEW = r'''/* ---------------- 版式 ----------------
 * 参考移动端卡片风：2x2 数值卡片 + 两行开关
 * 屏幕 320x240：
 *   (8,8)   温度 148x62      (164,8)  湿度 148x62
 *   (8,76)  光照 148x62      (164,76) 人体 148x62
 *   (8,146) 风扇 304x40      (8,192)  灯   304x40
 */
#define C_BG     0x0861
#define C_CARD   0x1927
#define C_LINE   0x2144
#define C_WHITE  0xFFFF
#define C_DIM    0x8C71
#define C_CYAN   0x07FF
#define C_BLUE   0x2A7F
#define C_GREEN  0x07E0
#define C_ORANGE 0xFD20
#define C_GRAY   0x4208

static void fill_circle(int cx, int cy, int r, uint16_t color)
{
    int dy;
    for (dy = -r; dy <= r; dy++) {
        int dx = r;
        while (dx > 0 && dx * dx + dy * dy > r * r) dx--;
        if (dx > 0) lcd_fill(cx - dx, cy + dy, cx + dx, cy + dy, color);
    }
}

static void round_rect(int x, int y, int w, int h, int r, uint16_t color)
{
    lcd_fill(x + r, y, x + w - r, y + h, color);
    lcd_fill(x, y + r, x + r, y + h - r, color);
    lcd_fill(x + w - r, y + r, x + w, y + h - r, color);
    fill_circle(x + r, y + r, r, color);
    fill_circle(x + w - r - 1, y + r, r, color);
    fill_circle(x + r, y + h - r - 1, r, color);
    fill_circle(x + w - r - 1, y + h - r - 1, r, color);
}

/* 图标：温度（温度计） */
static void icon_temp(int x, int y, uint16_t c)
{
    lcd_fill(x + 5, y, x + 9, y + 10, c);
    fill_circle(x + 7, y + 13, 5, c);
}

/* 图标：湿度（水滴） */
static void icon_hum(int x, int y, uint16_t c)
{
    fill_circle(x + 7, y + 11, 6, c);
    lcd_fill(x + 6, y, x + 9, y + 6, c);
    lcd_fill(x + 5, y + 2, x + 10, y + 5, c);
}

/* 图标：光照（太阳） */
static void icon_sun(int x, int y, uint16_t c)
{
    fill_circle(x + 7, y + 7, 4, c);
    lcd_fill(x + 6, y - 2, x + 9, y + 1, c);
    lcd_fill(x + 6, y + 14, x + 9, y + 17, c);
    lcd_fill(x - 2, y + 6, x + 1, y + 9, c);
    lcd_fill(x + 14, y + 6, x + 17, y + 9, c);
}

/* 图标：人体 */
static void icon_person(int x, int y, uint16_t c)
{
    fill_circle(x + 7, y + 3, 3, c);
    lcd_fill(x + 3, y + 8, x + 12, y + 16, c);
}

/* 图标：风扇 */
static void icon_fan(int x, int y, uint16_t c)
{
    fill_circle(x + 7, y + 7, 2, c);
    fill_circle(x + 7, y + 1, 3, c);
    fill_circle(x + 1, y + 10, 3, c);
    fill_circle(x + 13, y + 10, 3, c);
}

/* 图标：灯 */
static void icon_bulb(int x, int y, uint16_t c)
{
    fill_circle(x + 7, y + 6, 5, c);
    lcd_fill(x + 5, y + 12, x + 10, y + 15, c);
}

/* 开关：w=44 h=20 */
static void toggle(int x, int y, int on)
{
    uint16_t track = on ? C_BLUE : C_GRAY;
    round_rect(x, y, 44, 20, 10, track);
    fill_circle(x + (on ? 33 : 11), y + 10, 7, C_WHITE);
}

/* 单张数值卡片 */
static void card_value(int x, int y, const char *label, const char *value,
                       const char *unit, uint16_t vcolor, int icon_kind)
{
    round_rect(x, y, 148, 62, 10, C_CARD);
    switch (icon_kind) {
    case 0: icon_temp(x + 10, y + 10, vcolor); break;
    case 1: icon_hum(x + 10, y + 10, vcolor); break;
    case 2: icon_sun(x + 10, y + 10, vcolor); break;
    default: icon_person(x + 10, y + 10, vcolor); break;
    }
    lcd_show_chinese(x + 36, y + 12, label, C_DIM, C_CARD, 16, 0);
    lcd_show_string(x + 12, y + 32, (const uint8_t *)value, vcolor, C_CARD, 24, 0);
    if (unit && unit[0]) lcd_show_string(x + 100, y + 40, (const uint8_t *)unit, vcolor, C_CARD, 16, 0);
}

static void draw_values(void)
{
    char buf[16];

    round_rect(0, 0, LCD_W, LCD_H, 0, C_BG);

    /* 温度 */
    snprintf(buf, sizeof(buf), "%.1f", g_temp < -90 ? 0.0f : g_temp);
    card_value(8, 8, "温度", buf, "C", C_CYAN, 0);

    /* 湿度 */
    snprintf(buf, sizeof(buf), "%.0f", g_hum < 0 ? 0.0f : g_hum);
    card_value(164, 8, "湿度", buf, "%", 0x5D9F, 1);

    /* 光照 */
    snprintf(buf, sizeof(buf), "%d", g_lux < 0 ? 0 : g_lux);
    card_value(8, 76, "光照", buf, "lx", C_ORANGE, 2);

    /* 人体 */
    card_value(164, 76, "人体", g_pir ? "有人" : "无人",
               "", g_pir ? C_GREEN : C_DIM, 3);

    /* 风扇 */
    {
        int on = (g_fan_duty > 0);
        uint16_t bg = on ? C_BLUE : C_CARD;
        round_rect(8, 146, 304, 40, 10, bg);
        icon_fan(20, 157, C_WHITE);
        lcd_show_chinese(44, 157, "风扇", C_WHITE, bg, 16, 0);
        lcd_show_chinese(180, 157, on ? "开" : "关", on ? C_WHITE : C_DIM, bg, 16, 0);
        toggle(252, 156, on);
    }

    /* 灯 */
    {
        int on = (g_led_on > 0);
        uint16_t bg = on ? C_BLUE : C_CARD;
        round_rect(8, 192, 304, 40, 10, bg);
        icon_bulb(20, 203, C_WHITE);
        lcd_show_chinese(44, 203, "灯", C_WHITE, bg, 16, 0);
        lcd_show_chinese(180, 203, on ? "开" : "关", on ? C_WHITE : C_DIM, bg, 16, 0);
        toggle(252, 202, on);
    }
}

static void dash_full(void)
{
    lcd_fill(0, 0, LCD_W, LCD_H, C_BG);
    draw_values();
}

'''
s = s[:start] + NEW + s[end:]
open(P, "w", encoding="utf-8").write(s)
print("已替换为新版式")
