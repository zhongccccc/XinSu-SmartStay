
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
