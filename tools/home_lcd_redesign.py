# -*- coding: utf-8 -*-
"""v19：重做 LCD 版式（简洁风），同时保留 PIR 只上报不控灯的改动。"""
P = r"E:\zhikong\home_app\zh_home_v9.c"
s = open(P, encoding="utf-8").read()

start = s.index("/* ---------------- 版式 ---------------- */")
end = s.index("/* ---------------- shell ---------------- */")

NEW = r'''/* ---------------- 版式 ---------------- */
#define C_BG     0x0861   /* 深蓝黑 */
#define C_CARD   0x10E4
#define C_LINE   0x2124
#define C_WHITE  0xFFFF
#define C_DIM    0x8C71
#define C_CYAN   0x07FF
#define C_GREEN  0x07E0
#define C_RED    0xF800
#define C_YELLOW 0xFFE0
#define C_ORANGE 0xFD20

static void draw_top(void)
{
    lcd_fill(0, 0, LCD_W, LCD_H, C_BG);
    lcd_fill(0, 0, LCD_W, 4, C_CYAN);            /* 顶部细亮线 */
    lcd_show_chinese(12, 8, "客房环境", C_DIM, C_BG, 16, 0);
    lcd_show_string(232, 10, "ZHI KONG", C_LINE, C_BG, 12, 0);
    lcd_draw_line(0, 30, LCD_W, 30, C_LINE);
}

static void draw_values(void)
{
    /* 温度：主视觉 */
    lcd_fill(10, 38, 186, 140, C_BG);
    lcd_show_float_num1(22, 48, g_temp, 4, C_WHITE, C_BG, 32);
    lcd_draw_circle(150, 58, 3, C_WHITE);        /* 度数的小圆点 */
    lcd_show_string(158, 54, "C", C_DIM, C_BG, 24, 0);
    lcd_show_chinese(22, 112, "温度", C_DIM, C_BG, 16, 0);

    /* 湿度：次要 */
    lcd_fill(196, 38, 314, 140, C_BG);
    lcd_show_float_num1(200, 52, g_hum, 4, C_CYAN, C_BG, 24);
    lcd_show_string(276, 58, "%", C_CYAN, C_BG, 16, 0);
    lcd_show_chinese(200, 112, "湿度", C_DIM, C_BG, 16, 0);

    /* 中间分隔线 */
    lcd_draw_line(186, 44, 186, 126, C_LINE);
    lcd_draw_line(0, 146, LCD_W, 146, C_LINE);

    /* 底部三栏 */
    lcd_fill(0, 150, LCD_W, LCD_H, C_BG);
    lcd_draw_line(106, 154, 106, LCD_H - 6, C_LINE);
    lcd_draw_line(213, 154, 213, LCD_H - 6, C_LINE);

    lcd_show_chinese(14, 154, "光照", C_DIM, C_BG, 16, 0);
    lcd_show_int_num(14, 178, (uint16_t)(g_lux < 0 ? 0 : g_lux), 4, C_YELLOW, C_BG, 24);

    lcd_show_chinese(120, 154, "燃气", C_DIM, C_BG, 16, 0);
    if (g_gas > 2500) lcd_show_chinese(120, 178, "报警", C_RED, C_BG, 24, 0);
    else              lcd_show_chinese(120, 178, "良好", C_GREEN, C_BG, 24, 0);

    lcd_show_chinese(226, 154, "人体", C_DIM, C_BG, 16, 0);
    if (g_pir) lcd_show_chinese(226, 178, "有人", C_ORANGE, C_BG, 24, 0);
    else       lcd_show_chinese(226, 178, "无人", C_DIM, C_BG, 24, 0);
}

static void dash_full(void)
{
    draw_top();
    draw_values();
}

'''
s = s[:start] + NEW + s[end:]

# 主循环里旧的 hero_sync/footer_sync 调用改成整体重绘（数据变化不频繁，1 秒一次不闪）
s = s.replace("if (inited_lcd) { hero_sync(); footer_sync(); }", "if (inited_lcd) { draw_values(); }")
s = s.replace("if (inited_lcd) footer_sync();", "if (inited_lcd) { draw_values(); }")
s = s.replace("if (inited_lcd) { footer_sync(); }", "if (inited_lcd) { draw_values(); }")
s = s.replace("lcd_fill(0, 0, LCD_W, LCD_H, C_BG);\n    draw_header();\n    hero_frame();\n    footer_frame();", "dash_full();")

open(P, "w", encoding="utf-8").write(s)
print("版式已替换")

# 检查是否还有旧函数调用
for bad in ("hero_sync", "footer_sync", "footer_cell", "draw_header", "hero_frame", "footer_frame"):
    if bad in s:
        print("!! 仍有旧引用:", bad)
