# -*- coding: utf-8 -*-
"""v46：板载 NFC 刷卡——已绑定的卡开门；新卡自动绑定到最近下发的凭证。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

# 1) 绑定函数
anchor = "static void cred_clear(void)"
BIND = '''/* 把一张卡绑定到"最近下发且还没绑卡"的凭证；成功返回绑定到的房间号 */
static int cred_bind_card(const char *uid, char *room_out)
{
    int bound = 0;
    if (!uid || !uid[0]) return 0;
    if (g_cred_mutex) osMutexAcquire(g_cred_mutex, osWaitForever);
    for (int i = 0; i < ZK_CODE_MAX; i++) {
        if (g_creds[i].used && g_creds[i].card[0] == '\\0') {
            snprintf(g_creds[i].card, sizeof(g_creds[i].card), "%s", uid);
            if (room_out) snprintf(room_out, 8, "%s", g_creds[i].room);
            bound = 1;
            break;
        }
    }
    if (g_cred_mutex) osMutexRelease(g_cred_mutex);
    return bound;
}

'''
assert anchor in s
s = s.replace(anchor, BIND + anchor, 1)

# 2) 主循环刷卡逻辑：先比对，再尝试绑定
old = '''                    if (cred_check_card(uid)) {
                        do_open("card");
                    }
                    g_oled_dirty = 1;'''
new = '''                    if (cred_check_card(uid)) {
                        do_open("card");
                    } else {
                        char room[8];
                        if (cred_bind_card(uid, room)) {
                            zk_print("ZK|EVT|CARDBIND|%s|%s\\r\\n", room, uid);
                            do_open("card");
                        } else {
                            zk_print("ZK|EVT|CARDDENY|%s\\r\\n", uid);
                        }
                    }
                    g_oled_dirty = 1;'''
assert old in s
s = s.replace(old, new, 1)

# 3) 发凭证时清空旧卡位（避免绑定到旧凭证）
s = s.replace('''        snprintf(c->card, sizeof(c->card), "%s", (card && strcmp(card, "-")) ? card : "");''',
              '''        /* 一体机给的卡号如果是占位值（CARDxxxx / "-"），就当"待绑定" */
        if (card && strcmp(card, "-") != 0 && strncmp(card, "CARD", 4) != 0) {
            snprintf(c->card, sizeof(c->card), "%s", card);
        } else {
            c->card[0] = '\\0';
        }''', 1)

s = s.replace("rk2206-lock-v45", "rk2206-lock-v46")
open(P, "w", encoding="utf-8").write(s)
print("patched v46")
