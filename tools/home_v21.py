# -*- coding: utf-8 -*-
"""v21：加 zh inv / zh madctl 命令，现场调屏幕反色与色序。"""
import re

# ---------- lcd.c / lcd.h: 导出反色与 MADCTL ----------
C = "/home/openharmony/txsmartropenharmony/applications/sample/wifi-iot/app/zhikong_home/lcd.c"
H = "/home/openharmony/txsmartropenharmony/applications/sample/wifi-iot/app/zhikong_home/lcd.h"

# 这些文件在容器里，用 docker exec 写；这里只生成 python 补丁脚本
PATCH = r'''
import io, re
c = open("lcd.c", encoding="utf-8", errors="replace").read()
if "void lcd_invert" not in c:
    c = c.replace("unsigned int lcd_deinit()",
"""void lcd_invert(unsigned char on)
{
    lcd_wr_reg(on ? 0x21 : 0x20);   /* 0x21=INVON 0x20=INVOFF */
}

void lcd_madctl(unsigned char v)
{
    lcd_wr_reg(0x36);
    lcd_wr_data8(v);
}

unsigned int lcd_deinit()""", 1)
    open("lcd.c", "w", encoding="utf-8").write(c)
    print("lcd.c 已加 lcd_invert / lcd_madctl")

h = open("lcd.h", encoding="utf-8", errors="replace").read()
if "lcd_invert" not in h:
    h = h.replace("unsigned int lcd_deinit();",
"""void lcd_invert(unsigned char on);
void lcd_madctl(unsigned char v);
unsigned int lcd_deinit();""", 1)
    open("lcd.h", "w", encoding="utf-8").write(h)
    print("lcd.h 已导出")
'''

open(r"E:\zhikong\tools\_lcd_patch.py", "w", encoding="utf-8").write(PATCH)

# ---------- zh_home.c: 加命令 ----------
P = r"E:\zhikong\home_app\zh_home_v9.c"
s = open(P, encoding="utf-8").read()
s = s.replace('ZH_VER           "rk2206-home-v20"', 'ZH_VER           "rk2206-home-v21"')

OLD = '''    } else if (strcmp(sub, "light") == 0) {'''
NEW = '''    } else if (strcmp(sub, "inv") == 0) {
        int on = (argc > 2) ? atoi(argv[2]) : 1;
        lcd_invert((unsigned char)(on ? 1 : 0));
        if (inited_lcd) dash_full();
        zh_print("ZH|ACK|INV|%d\\r\\n", on);
    } else if (strcmp(sub, "madctl") == 0) {
        int v = (argc > 2) ? (int)strtol(argv[2], NULL, 0) : 0x54;
        lcd_madctl((unsigned char)v);
        if (inited_lcd) dash_full();
        zh_print("ZH|ACK|MADCTL|0x%02X\\r\\n", v);
    } else if (strcmp(sub, "light") == 0) {'''

if OLD in s and '"inv"' not in s:
    s = s.replace(OLD, NEW, 1)
    print("zh_home.c 已加 inv / madctl")
elif '"inv"' in s:
    print("已存在")

open(P, "w", encoding="utf-8").write(s)
