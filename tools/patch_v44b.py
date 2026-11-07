# -*- coding: utf-8 -*-
"""v44b：NFC 集成到主循环 + 房卡比对 + zk nfc 测试命令。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

# 1) 房卡比对
anchor = "static void cred_add(const char *room"
CARDCHK = '''static int cred_check_card(const char *uid)
{
    int hit = 0;
    if (!uid || !uid[0]) return 0;
    if (g_cred_mutex) osMutexAcquire(g_cred_mutex, osWaitForever);
    for (int i = 0; i < ZK_CODE_MAX; i++) {
        if (g_creds[i].used && g_creds[i].card[0] &&
            strcasecmp(g_creds[i].card, uid) == 0) {
            hit = 1;
            break;
        }
    }
    if (g_cred_mutex) osMutexRelease(g_cred_mutex);
    return hit;
}

'''
assert anchor in s
s = s.replace(anchor, CARDCHK + anchor, 1)

# 2) 主循环：NFC 轮询
anchor2 = "        if (!g_fp_suspend && g_lock_state == 0 && t - fp_tick > 800) {"
NFC_POLL = '''        /* 板载 NFC：锁着时轮询寻卡 */
        if (g_nfc_ok && g_lock_state == 0 && t - nfc_tick > 400) {
            nfc_tick = t;
            char uid[16];
            if (nfc_read_uid(uid, sizeof(uid))) {
                if (strcmp(uid, g_last_uid) != 0) {
                    snprintf(g_last_uid, sizeof(g_last_uid), "%s", uid);
                    g_card_reads++;
                    zk_print("ZK|EVT|CARD|%s\\r\\n", uid);
                    if (cred_check_card(uid)) {
                        do_open("card");
                    }
                    g_oled_dirty = 1;
                }
            } else {
                g_last_uid[0] = '\\0';
            }
        }

'''
assert anchor2 in s
s = s.replace(anchor2, NFC_POLL + anchor2, 1)

# 3) 局部变量
s = s.replace("    unsigned int oled_tick = 0;",
              "    unsigned int oled_tick = 0;\n    unsigned int nfc_tick = 0;\n    unsigned int nfc_boot = 0;", 1)

# 4) 延迟初始化 NFC
s = s.replace('''        /* ---- OLED：初始化重试 + 内容变化时才刷新 ---- */''',
              '''        /* ---- NFC 延迟初始化 ---- */
        if (!g_nfc_ok && nfc_boot == 0 && t > 1200) {
            nfc_boot = 1;
            int ver = nfc_init();
            zk_print("[zk] nfc ver=0x%02X ok=%d\\r\\n", ver, g_nfc_ok);
        }

        /* ---- OLED：初始化重试 + 内容变化时才刷新 ---- */''', 1)

# 5) zk nfc 测试命令
anchor3 = '    } else if (strcmp(sub, "pt") == 0) {'
NFC_CMD = '''    } else if (strcmp(sub, "nfc") == 0) {
        if (!g_nfc_ok) {
            int ver = nfc_init();
            zk_print("ZK|ACK|NFC|INIT|ver=0x%02X|ok=%d\\r\\n", ver, g_nfc_ok);
        }
        char uid[16];
        int got = 0;
        for (int i = 0; i < 8 && !got; i++) {
            got = nfc_read_uid(uid, sizeof(uid));
            if (!got) usleep(120 * 1000);
        }
        if (got) zk_print("ZK|ACK|NFC|UID|%s\\r\\n", uid);
        else zk_print("ZK|ACK|NFC|NOCARD\\r\\n");
'''
assert anchor3 in s
s = s.replace(anchor3, NFC_CMD + anchor3, 1)

s = s.replace("rk2206-lock-v44", "rk2206-lock-v45")
open(P, "w", encoding="utf-8").write(s)
print("patched v45 (nfc integrated)")
