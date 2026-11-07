# -*- coding: utf-8 -*-
"""v17：按原理图修正 AW9523B 地址(0x59) 与 LED 位映射。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

# 1) 地址：AD0 接 +3.3V → 0x59
s = s.replace("#define AW9523_ADDR       0x58", "#define AW9523_ADDR       0x59   /* AD0=+3.3V */")

# 2) LED 初始化：增加 LED 模式寄存器（0=GPIO 推挽），并全灭
old_init = '''    aw9523_write(0x04, 0x00);      /* P0 全输出 */
    aw9523_write(0x05, 0x00);      /* P1 全输出 */
    aw9523_write(0x02, 0xFF);      /* P0 灭（低电平点亮，故写 1 灭） */
    aw9523_write(0x03, 0xFF);      /* P1 灭 */'''
new_init = '''    aw9523_write(0x12, 0x00);      /* P0 用 GPIO 模式（1=LED 调光模式） */
    aw9523_write(0x13, 0x00);      /* P1 同理 */
    aw9523_write(0x04, 0x00);      /* P0 全输出 */
    aw9523_write(0x05, 0x00);      /* P1 全输出 */
    aw9523_write(0x02, 0xFF);      /* P0 灭（低电平点亮 → 写 1 灭） */
    aw9523_write(0x03, 0xFF);      /* P1 灭 */'''
assert old_init in s, "led_init 片段未找到"
s = s.replace(old_init, new_init, 1)

# 3) led_show：按原理图映射
old_show = '''static void led_show(unsigned int mask)
{
    /* 按位点亮：bit n → 对应 LED */
    unsigned int p0 = mask & 0xFF;
    unsigned int p1 = (mask >> 8) & 0xFF;
    aw9523_write(0x02, (unsigned char)(~p0));
    aw9523_write(0x03, (unsigned char)(~p1));
}'''
new_show = '''/* 原理图映射：
 *   TK_LED1..4  = P1_0..P1_3   （寄存器 0x03，bit0..3）
 *   TK_LED5..12 = P0_0..P0_7   （寄存器 0x02，bit0..7）
 * 键位 bit n（n=0..11）对应第 n+1 颗灯。低电平点亮。 */
static void led_show(unsigned int mask)
{
    unsigned int p0 = 0, p1 = 0;
    for (int i = 0; i < 12; i++) {
        if (mask & (1u << i)) {
            if (i < 4) {
                p1 |= (1u << i);
            } else {
                p0 |= (1u << (i - 4));
            }
        }
    }
    aw9523_write(0x02, (unsigned char)(~p0 & 0xFF));
    aw9523_write(0x03, (unsigned char)(~p1 & 0xFF));
}'''
assert old_show in s, "led_show 片段未找到"
s = s.replace(old_show, new_show, 1)

s = s.replace("rk2206-lock-v16", "rk2206-lock-v17")
open(P, "w", encoding="utf-8").write(s)
print("patched v17")
