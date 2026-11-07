# -*- coding: utf-8 -*-
"""v23：软件取反配色（这块屏硬件反色），并加 zh invsw 现场开关。"""
import re

P = r"E:\zhikong\home_app\zh_home_v9.c"
s = open(P, encoding="utf-8").read()

s = s.replace('ZH_VER           "rk2206-color-test"', 'ZH_VER           "rk2206-home-v23"')
s = s.replace('ZH_VER           "rk2206-home-v21"', 'ZH_VER           "rk2206-home-v23"')

start = s.index("/* ---------------- 版式 ----------------")
end = s.index("/* ---------------- shell ---------------- */")

NEW = r'''/* ---------------- 版式 ----------------
 * 注意：这块 2.4" 屏是**硬件反色**显示的（实测橙色→蓝色），
 * 所以这里所有颜色都过一层 SC() 取反，实际显示才是设计色。
 * 用 `zh invsw 0` 可关掉取反（若换了不反色的屏）。
 */
static int g_inv = 1;
#define SC(c) ((uint16_t)(g_inv ? (~(c)) : (c)))

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
#define C_BLACK  0x0000

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
    if (r <= 0) {
        lcd_fill(x, y, x + w - 1, y + h - 1, color);
        return;
    }
    lcd_fill(x + r, y, x + w - r - 1, y + h - 1, color);
    lcd_fill(x, y + r, x + r - 1, y + h - r - 1, color);
    lcd_fill(x + w - r, y + r, x + w - 1, y + h - r - 1, color);
    fill_circle(x + r, y + r, r, color);
    fill_circle(x + w - r - 1, y + r, r, color);
    fill_circle(x + r, y + h - r - 1, r, color);
    fill_circle(x + w - r - 1, y + h - r - 1, r, color);
}

static void icon_temp(int x, int y, uint16_t c)
{
    lcd_fill(x + 5, y, x + 9, y + 10, c);
    fill_circle(x + 7, y + 13, 5, c);
}

static void icon_hum(int x, int y, uint16_t c)
{
    fill_circle(x + 7, y + 11, 6, c);
    lcd_fill(x + 6, y, x + 9, y + 6, c);
    lcd_fill(x + 5, y + 2, x + 10, y + 5, c);
}

static void icon_sun(int x, int y, uint16_t c)
{
    fill_circle(x + 7, y + 7, 4, c);
    lcd_fill(x + 6, y - 2, x + 9, y + 1, c);
    lcd_fill(x + 6, y + 14, x + 9, y + 17, c);
    lcd_fill(x - 2, y + 6, x + 1, y + 9, c);
    lcd_fill(x + 14, y + 6, x + 17, y + 9, c);
}

static void icon_person(int x, int y, uint16_t c)
{
    fill_circle(x + 7, y + 3, 3, c);
    lcd_fill(x + 3, y + 8, x + 12, y + 16, c);
}

static void icon_fan(int x, int y, uint16_t c)
{
    fill_circle(x + 7, y + 7, 2, c);
    fill_circle(x + 7, y + 1, 3, c);
    fill_circle(x + 1, y + 10, 3, c);
    fill_circle(x + 13, y + 10, 3, c);
}

static void icon_bulb(int x, int y, uint16_t c)
{
    fill_circle(x + 7, y + 6, 5, c);
    lcd_fill(x + 5, y + 12, x + 10, y + 15, c);
}

static void toggle(int x, int y, int on)
{
    round_rect(x, y, 44, 20, 10, SC(on ? C_BLUE : C_GRAY));
    fill_circle(x + (on ? 33 : 11), y + 10, 7, SC(C_WHITE));
}

static void card_value(int x, int y, const char *label, const char *value,
                       const char *unit, uint16_t vcolor, int icon_kind)
{
    round_rect(x, y, 148, 62, 10, SC(C_CARD));
    switch (icon_kind) {
    case 0: icon_temp(x + 10, y + 10, SC(vcolor)); break;
    case 1: icon_hum(x + 10, y + 10, SC(vcolor)); break;
    case 2: icon_sun(x + 10, y + 10, SC(vcolor)); break;
    default: icon_person(x + 10, y + 10, SC(vcolor)); break;
    }
    lcd_show_chinese(x + 36, y + 12, label, SC(C_DIM), SC(C_CARD), 16, 0);
    lcd_show_string(x + 12, y + 32, (const uint8_t *)value, SC(vcolor), SC(C_CARD), 24, 0);
    if (unit && unit[0]) {
        lcd_show_string(x + 100, y + 40, (const uint8_t *)unit, SC(vcolor), SC(C_CARD), 16, 0);
    }
}

static void draw_values(void)
{
    char buf[16];

    round_rect(0, 0, LCD_W, LCD_H, 0, SC(C_BG));

    snprintf(buf, sizeof(buf), "%.1f", g_temp < -90 ? 0.0f : g_temp);
    card_value(8, 8, "温度", buf, "C", C_CYAN, 0);

    snprintf(buf, sizeof(buf), "%.0f", g_hum < 0 ? 0.0f : g_hum);
    card_value(164, 8, "湿度", buf, "%", 0x5D9F, 1);

    snprintf(buf, sizeof(buf), "%d", g_lux < 0 ? 0 : g_lux);
    card_value(8, 76, "光照", buf, "lx", C_ORANGE, 2);

    card_value(164, 76, "人体", g_pir ? "有人" : "无人",
               "", g_pir ? C_GREEN : C_DIM, 3);

    {
        int on = (g_fan_duty > 0);
        uint16_t bg = SC(on ? C_BLUE : C_CARD);
        round_rect(8, 146, 304, 40, 10, bg);
        icon_fan(20, 157, SC(C_WHITE));
        lcd_show_chinese(44, 157, "风扇", SC(C_WHITE), bg, 16, 0);
        lcd_show_chinese(180, 157, on ? "开" : "关", SC(on ? C_WHITE : C_DIM), bg, 16, 0);
        toggle(252, 156, on);
    }

    {
        int on = (g_led_on > 0);
        uint16_t bg = SC(on ? C_BLUE : C_CARD);
        round_rect(8, 192, 304, 40, 10, bg);
        icon_bulb(20, 203, SC(C_WHITE));
        lcd_show_chinese(44, 203, "灯", SC(C_WHITE), bg, 16, 0);
        lcd_show_chinese(180, 203, on ? "开" : "关", SC(on ? C_WHITE : C_DIM), bg, 16, 0);
        toggle(252, 202, on);
    }
}

static void dash_full(void)
{
    lcd_fill(0, 0, LCD_W - 1, LCD_H - 1, SC(C_BG));
    draw_values();
}

'''
s = s[:start] + NEW + s[end:]

# 加 invsw 命令
OLD_CMD = '''    } else if (strcmp(sub, "inv") == 0) {'''
NEW_CMD = '''    } else if (strcmp(sub, "invsw") == 0) {
        g_inv = (argc > 2) ? (atoi(argv[2]) ? 1 : 0) : 1;
        if (inited_lcd) dash_full();
        zh_print("ZH|ACK|INVSW|%d\\r\\n", g_inv);
    } else if (strcmp(sub, "inv") == 0) {'''
if OLD_CMD in s and '"invsw"' not in s:
    s = s.replace(OLD_CMD, NEW_CMD, 1)
    print("已加 invsw 命令")

# 确保 g_inv 在命令之前声明（版式段在 shell 之前，OK）
open(P, "w", encoding="utf-8").write(s)
print("v23 版式已写入")
