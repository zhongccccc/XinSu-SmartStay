# -*- coding: utf-8 -*-
"""v43：OLED 布局重做——小锁图标在左上角，密码用圆点遮罩显示。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

# 1) 替换 draw_lock（更紧凑：22x16）
start = s.index("static void draw_lock(int x, int y, int open)")
end = s.index("static void oled_render(void)")
NEW_LOCK = '''static void draw_lock(int x, int y, int open)
{
    /* 锁体 18x11 */
    rect(x, y + 7, 18, 11, 1);
    rect(x + 5, y + (open ? 9 : 11), 8, 6, 0);
    /* 锁梁 */
    if (open) {
        rect(x + 13, y, 4, 8, 1);
    } else {
        rect(x + 3, y, 3, 8, 1);
        rect(x + 8, y, 3, 8, 1);
        rect(x + 3, y, 8, 3, 1);
    }
}

static void draw_dot(int cx, int cy, int r)
{
    for (int dy = -r; dy <= r; dy++) {
        for (int dx = -r; dx <= r; dx++) {
            if (dx * dx + dy * dy <= r * r) {
                px(cx + dx, cy + dy, 1);
            }
        }
    }
}

'''
s = s[:start] + NEW_LOCK + s[end:]

# 2) 替换 oled_render（圆点遮罩 + 不重叠布局）
start = s.index("static void oled_render(void)")
end = s.index("/* ================= 凭证 ================= */")
NEW_RENDER = '''static void oled_render(void)
{
    if (!g_oled_ok) return;
    memset(g_fb, 0, sizeof(g_fb));

    /* 左上：锁状态图标（22x18） */
    draw_lock(2, 1, g_lock_state);

    /* 右上：开锁状态小方块 */
    if (g_lock_state) {
        rect(118, 4, 8, 8, 0);
        for (int i = 0; i < 8; i++) { px(122 - i, 4 + i, 1); }
    } else {
        rect(118, 4, 8, 8, 1);
        rect(120, 6, 4, 4, 0);
    }

    /* 分隔线 */
    rect(0, 21, 128, 1, 1);

    /* 密码：6 个槽位，已输入的画圆点（不显示真实数字） */
    for (int i = 0; i < PIN_LEN; i++) {
        int cx = 12 + i * 20;
        if (i < g_pin_len) {
            draw_dot(cx, 38, 5);
        } else {
            rect(cx - 5, 37, 10, 3, 1);      /* 未输入：短横 */
        }
    }

    /* 底部提示条 */
    rect(0, 54, 128, 1, 1);
    if (g_pin_len > 0 && g_pin_len < PIN_LEN) {
        for (int i = 0; i < g_pin_len; i++) rect(4 + i * 6, 58, 4, 2, 1);
    } else if (g_pin_len == PIN_LEN) {
        rect(4, 58, 120, 2, 1);              /* 输满 6 位 */
    }
    oled_flush();
}

'''
s = s[:start] + NEW_RENDER + s[end:]

s = s.replace("rk2206-lock-v42", "rk2206-lock-v43")
open(P, "w", encoding="utf-8").write(s)
print("patched v43")
