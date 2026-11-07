# -*- coding: utf-8 -*-
"""v22：录入期间暂停自动识别轮询，避免覆盖 buffer。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

# 1) 全局标志
s = s.replace("static volatile int g_pwm_ready = 0;",
              "static volatile int g_pwm_ready = 0;\nstatic volatile int g_fp_suspend = 0;   /* 录入期间暂停轮询 */", 1)

# 2) 轮询处加判断
s = s.replace("if (g_lock_state == 0 && t - fp_tick > 800) {",
              "if (!g_fp_suspend && g_lock_state == 0 && t - fp_tick > 800) {", 1)

# 3) en1 / en2 期间挂起
s = s.replace('''    } else if (strcmp(sub, "en1") == 0) {
        int ok = fp_capture_to(1);
        zk_print("ZK|ACK|EN1|%s\\r\\n", ok ? "OK" : "ERR");''',
              '''    } else if (strcmp(sub, "en1") == 0) {
        g_fp_suspend = 1;
        int ok = fp_capture_to(1);
        zk_print("ZK|ACK|EN1|%s\\r\\n", ok ? "OK" : "ERR");''', 1)
s = s.replace('''    } else if (strcmp(sub, "en2") == 0) {
        unsigned int page = (argc > 2) ? (unsigned int)atoi(argv[2]) : 0;
        int c2 = fp_capture_to(2);
        int ok = c2 && fp_enroll_finish(page);
        zk_print("ZK|ACK|EN2|%s|id=%u\\r\\n", ok ? "OK" : "ERR", page);''',
              '''    } else if (strcmp(sub, "en2") == 0) {
        g_fp_suspend = 1;
        unsigned int page = (argc > 2) ? (unsigned int)atoi(argv[2]) : 0;
        int c2 = fp_capture_to(2);
        int reg = c2 ? fp_enroll_finish(page) : -1;
        zk_print("ZK|ACK|EN2|%s|c2=%d|regist=%d|id=%u\\r\\n",
                 (c2 && reg) ? "OK" : "ERR", c2, reg, page);
        g_fp_suspend = 0;''', 1)

# 4) fpid 命令也挂起
s = s.replace('''    } else if (strcmp(sub, "fpid") == 0) {
        int id = fp_try_match();''',
              '''    } else if (strcmp(sub, "fpid") == 0) {
        g_fp_suspend = 1;
        int id = fp_try_match();
        g_fp_suspend = 0;''', 1)

s = s.replace("rk2206-lock-v21", "rk2206-lock-v22")
open(P, "w", encoding="utf-8").write(s)
print("patched v22")
