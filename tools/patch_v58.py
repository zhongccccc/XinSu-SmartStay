# -*- coding: utf-8 -*-
"""v58：按房间作废凭证；绑卡绑定最近下发的那条；保留 revoke 全部的能力。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

# 1) 凭证结构加序号
s = s.replace('''typedef struct {
    char code[16];
    char card[24];
    char room[8];
    int  ttl_min;
    int  used;
} zk_cred_t;''',
'''typedef struct {
    char code[16];
    char card[24];
    char room[8];
    int  ttl_min;
    int  used;
    unsigned int seq;      /* 下发序号，用于"绑定最近一条" */
} zk_cred_t;
static unsigned int g_cred_seq = 0;''', 1)

# 2) cred_add 记录序号
s = s.replace('''        c->ttl_min = ttl;
        c->used = 1;''',
'''        c->ttl_min = ttl;
        c->used = 1;
        c->seq = ++g_cred_seq;''', 1)

# 3) 新增按房间作废
anchor = "static void cred_clear(void)"
REVOKE_ROOM = '''/* 只作废某个房间的凭证；返回作废条数 */
static int cred_revoke_room(const char *room)
{
    int n = 0;
    if (!room || !room[0]) return 0;
    if (g_cred_mutex) osMutexAcquire(g_cred_mutex, osWaitForever);
    for (int i = 0; i < ZK_CODE_MAX; i++) {
        if (g_creds[i].used && strcmp(g_creds[i].room, room) == 0) {
            memset(&g_creds[i], 0, sizeof(g_creds[i]));
            n++;
        }
    }
    if (g_cred_mutex) osMutexRelease(g_cred_mutex);
    return n;
}

'''
assert anchor in s
s = s.replace(anchor, REVOKE_ROOM + anchor, 1)

# 4) 绑卡改成"绑定序号最大且未绑卡"的那条
old_bind = '''    for (int i = 0; i < ZK_CODE_MAX; i++) {
        if (g_creds[i].used && g_creds[i].card[0] == '\\0') {
            snprintf(g_creds[i].card, sizeof(g_creds[i].card), "%s", uid);
            if (room_out) snprintf(room_out, 8, "%s", g_creds[i].room);
            bound = 1;
            break;
        }
    }'''
new_bind = '''    int best = -1;
    unsigned int best_seq = 0;
    for (int i = 0; i < ZK_CODE_MAX; i++) {
        if (g_creds[i].used && g_creds[i].card[0] == '\\0' && g_creds[i].seq >= best_seq) {
            best_seq = g_creds[i].seq;
            best = i;
        }
    }
    if (best >= 0) {
        snprintf(g_creds[best].card, sizeof(g_creds[best].card), "%s", uid);
        if (room_out) snprintf(room_out, 8, "%s", g_creds[best].room);
        bound = 1;
    }'''
assert old_bind in s
s = s.replace(old_bind, new_bind, 1)

# 5) zk revoke [room]
old_rev = '''    } else if (strcmp(sub, "revoke") == 0) {
        cred_clear();
        zk_print("ZK|ACK|REVOKE|OK\\r\\n");'''
new_rev = '''    } else if (strcmp(sub, "revoke") == 0) {
        if (argc > 2) {
            int n = cred_revoke_room(argv[2]);
            zk_print("ZK|ACK|REVOKE|OK|room=%s|n=%d\\r\\n", argv[2], n);
        } else {
            cred_clear();
            zk_print("ZK|ACK|REVOKE|OK|all\\r\\n");
        }'''
assert old_rev in s
s = s.replace(old_rev, new_rev, 1)

s = s.replace("rk2206-lock-v57", "rk2206-lock-v58")
open(P, "w", encoding="utf-8").write(s)
print("patched v58")
