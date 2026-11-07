# -*- coding: utf-8 -*-
"""v22：颜色自检图（6 条标准色条），用来确定屏幕真实的颜色映射。"""
P = r"E:\zhikong\home_app\zh_home_v9.c"
s = open(P, encoding="utf-8").read()

s = s.replace('ZH_VER           "rk2206-home-v21"', 'ZH_VER           "rk2206-color-test"')

# 在 dash_full 里改成画色条
OLD = '''static void dash_full(void)
{
    lcd_fill(0, 0, LCD_W, LCD_H, C_BG);
    draw_values();
}'''

NEW = '''/* 颜色自检：屏幕从上到下 6 条色条
 * 1 白 0xFFFF | 2 红 0xF800 | 3 绿 0x07E0
 * 4 蓝 0x001F | 5 黑 0x0000 | 6 灰 0x8410
 */
static void color_test(void)
{
    lcd_fill(0,   0, LCD_W - 1,  39, 0xFFFF);
    lcd_fill(0,  40, LCD_W - 1,  79, 0xF800);
    lcd_fill(0,  80, LCD_W - 1, 119, 0x07E0);
    lcd_fill(0, 120, LCD_W - 1, 159, 0x001F);
    lcd_fill(0, 160, LCD_W - 1, 199, 0x0000);
    lcd_fill(0, 200, LCD_W - 1, 239, 0x8410);
}

static void dash_full(void)
{
    color_test();
}'''

if OLD in s:
    s = s.replace(OLD, NEW, 1)
    print("已改为颜色自检")
elif "color_test" in s:
    print("已存在")
else:
    print("!! 未匹配 dash_full")

open(P, "w", encoding="utf-8").write(s)
