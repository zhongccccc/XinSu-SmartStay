# -*- coding: utf-8 -*-
"""给 zk_lock.c 插入：键盘时序对比、指纹录入命令。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

KEYTEST = '''/* ---------------- 键盘时序对比（调试用） ---------------- */
static unsigned int ttp_read_A(void)
{
    unsigned int v = 0;
    IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
    usleep(120);
    for (int i = 0; i < 16; i++) {
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
        usleep(60);
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
        usleep(60);
        IotGpioValue s = IOT_GPIO_VALUE0;
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        if (s == IOT_GPIO_VALUE0) v |= (1u << i);
        usleep(60);
    }
    return v;
}

static unsigned int ttp_read_B(void)
{
    unsigned int v = 0;
    for (int i = 0; i < 16; i++) {
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
        usleep(200);
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
        usleep(200);
        IotGpioValue s = IOT_GPIO_VALUE0;
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        if (s == IOT_GPIO_VALUE0) v |= (1u << i);
    }
    return v;
}

static unsigned int ttp_read_C(void)
{
    unsigned int v = 0;
    IoTGpioSetDir(PIN_TK_SDA, IOT_GPIO_DIR_OUT);
    IoTGpioSetOutputVal(PIN_TK_SDA, IOT_GPIO_VALUE1);
    IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
    usleep(100);
    IoTGpioSetOutputVal(PIN_TK_SDA, IOT_GPIO_VALUE0);
    usleep(100);
    IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
    usleep(100);
    IoTGpioSetDir(PIN_TK_SDA, IOT_GPIO_DIR_IN);
    for (int i = 0; i < 16; i++) {
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
        usleep(120);
        IotGpioValue s = IOT_GPIO_VALUE0;
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        if (s == IOT_GPIO_VALUE0) v |= (1u << i);
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
        usleep(120);
    }
    return v;
}

static void keytest(void)
{
    for (int round = 0; round < 6; round++) {
        unsigned int a = ttp_read_A();
        unsigned int b = ttp_read_B();
        unsigned int c = ttp_read_C();
        zk_print("ZK|KEYTEST|%d|A=0x%04X|B=0x%04X|C=0x%04X\\r\\n", round, a, b, c);
        usleep(120 * 1000);
    }
}

'''

FP_ENROLL = '''/* ---------------- 指纹录入 ---------------- */
static void fp_enroll1(void)
{
    unsigned char rsp[32] = {0};
    unsigned char pkt[32];
    int n;
    int len = fp_build(pkt, 0x01, NULL, 0);
    n = fp_cmd(pkt, len, rsp, sizeof(rsp));
    zk_print("ZK|FP|IMG1|%d|%02X\\r\\n", n, rsp[9]);
    if (n < 12 || rsp[9] != 0x00) { zk_print("ZK|FP|EN1|ERR|capture\\r\\n"); return; }
    unsigned char b1 = 0x01;
    memset(rsp, 0, sizeof(rsp));
    len = fp_build(pkt, 0x02, &b1, 1);
    n = fp_cmd(pkt, len, rsp, sizeof(rsp));
    zk_print("ZK|FP|TZ1|%d|%02X\\r\\n", n, rsp[9]);
    zk_print("ZK|FP|EN1|%s\\r\\n", (n >= 12 && rsp[9] == 0x00) ? "OK" : "ERR");
}

static void fp_enroll2(unsigned int page)
{
    unsigned char rsp[32] = {0};
    unsigned char pkt[32];
    int n;
    int len = fp_build(pkt, 0x01, NULL, 0);
    n = fp_cmd(pkt, len, rsp, sizeof(rsp));
    zk_print("ZK|FP|IMG2|%d|%02X\\r\\n", n, rsp[9]);
    if (n < 12 || rsp[9] != 0x00) { zk_print("ZK|FP|EN2|ERR|capture\\r\\n"); return; }

    unsigned char b2 = 0x02;
    memset(rsp, 0, sizeof(rsp));
    len = fp_build(pkt, 0x02, &b2, 1);
    n = fp_cmd(pkt, len, rsp, sizeof(rsp));
    zk_print("ZK|FP|TZ2|%d|%02X\\r\\n", n, rsp[9]);
    if (n < 12 || rsp[9] != 0x00) { zk_print("ZK|FP|EN2|ERR|tz2\\r\\n"); return; }

    memset(rsp, 0, sizeof(rsp));
    len = fp_build(pkt, 0x05, NULL, 0);
    n = fp_cmd(pkt, len, rsp, sizeof(rsp));
    zk_print("ZK|FP|REGMODEL|%d|%02X\\r\\n", n, rsp[9]);
    if (n < 12 || rsp[9] != 0x00) { zk_print("ZK|FP|EN2|ERR|match\\r\\n"); return; }

    unsigned char st[3] = {0x01, (unsigned char)(page >> 8), (unsigned char)(page & 0xFF)};
    memset(rsp, 0, sizeof(rsp));
    len = fp_build(pkt, 0x06, st, 3);
    n = fp_cmd(pkt, len, rsp, sizeof(rsp));
    zk_print("ZK|FP|STORE|%d|%02X\\r\\n", n, rsp[9]);
    zk_print("ZK|FP|EN2|%s|id=%u\\r\\n", (n >= 12 && rsp[9] == 0x00) ? "OK" : "ERR", page);
}

'''

anchor = "/* ---------------- 扫描 ---------------- */"
assert anchor in s
s = s.replace(anchor, KEYTEST + FP_ENROLL + anchor, 1)

# 命令绑定
old = '''    } else if (strcmp(sub, "fp") == 0) {'''
new = '''    } else if (strcmp(sub, "keytest") == 0) {
        keytest();
        zk_print("ZK|ACK|KEYTEST|OK\\r\\n");
    } else if (strcmp(sub, "en1") == 0) {
        fp_enroll1();
        zk_print("ZK|ACK|EN1|OK\\r\\n");
    } else if (strcmp(sub, "en2") == 0) {
        fp_enroll2(argc > 2 ? (unsigned int)atoi(argv[2]) : 0);
        zk_print("ZK|ACK|EN2|OK\\r\\n");
    } else if (strcmp(sub, "fp") == 0) {'''
assert old in s
s = s.replace(old, new, 1)

s = s.replace("rk2206-lock-v11", "rk2206-lock-v12")
open(P, "w", encoding="utf-8").write(s)
print("patched:", P)
print("keytest:", "keytest" in s, " en1:", '"en1"' in s, " v12:", "v12" in s)
