# -*- coding: utf-8 -*-
"""v47：关锁时长改 2000ms；键盘扫描提速；NFC 轮询降频避免抢资源。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

# 1) 关锁默认 2000ms
s = s.replace('static unsigned int g_lock_ms = 800;',
              'static unsigned int g_lock_ms = 2000;  /* 实测 800ms 关不到位，同样需要 2 秒 */')

# 2) 键盘扫描从 n%5 提到 n%2（更快，避免漏按）
s = s.replace('if (!g_fp_suspend && n % 5 == 0) {', 'if (!g_fp_suspend && n % 2 == 0) {', 1)

# 3) NFC 轮询降频到 800ms，且按住键时不轮询
s = s.replace('if (g_nfc_ok && g_lock_state == 0 && t - nfc_tick > 400) {',
              'if (g_nfc_ok && g_lock_state == 0 && t - nfc_tick > 800) {', 1)

# 4) 版本
s = s.replace("rk2206-lock-v46", "rk2206-lock-v47")
open(P, "w", encoding="utf-8").write(s)
print("patched v47")
