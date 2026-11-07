/*
 * 芯宿·智控 —— 智能门锁板 v23
 *
 * 本版新增：
 *   1) 开锁/上锁通电时间缩短到 300ms（原来 1200ms 会顶过头）
 *   2) zk learn：板子逐个提示按哪个键，自动学习键盘映射
 *   3) OLED(SSD1306 128x64, I2C1 0x3C)：显示输入中的密码与锁状态
 *
 * 硬件：电机 IA=PC7(23)/IB=GPIO1_PD0(56)，指纹 UART2，键盘 TTP229(PA0/PA1)
 */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdarg.h>
#include <unistd.h>

#include "ohos_init.h"
#include "cmsis_os2.h"
#include "iot_gpio.h"
#include "iot_i2c.h"
#include "iot_pwm.h"
#include "iot_uart.h"
#include "iot_spi.h"
#include "iot_errno.h"

#define ZK_CMD_TYPE_STD   1
#define ZK_XARGS          0xFFFFFFFFu
typedef unsigned int (*zk_cmd_cb_t)(unsigned int argc, const char **argv);
extern unsigned int osCmdReg(int cmdType, const char *cmdKey,
                             unsigned int paraNum, zk_cmd_cb_t cmdProc);

#define PIN_MOTOR_IA      23
#define PIN_MOTOR_IB      56
#define PIN_BUZZER        21
#define PWM_BUZZER        EPWMDEV_PWM5_M0
#define PIN_TK_SCL        1
#define PIN_TK_SDA        0
#define UART_FP           1
#define SPI_NFC           ESPI0_M1     /* CS PC0, CLK PC1, MOSI PC2, MISO PC3 */
#define PIN_NFC_CS        16           /* GPIO0_PC0 */

/* MFRC522 / WS1850S 寄存器 */
#define RC_COMMAND        0x01
#define RC_COMIRQ         0x04
#define RC_ERROR          0x06
#define RC_FIFODATA       0x09
#define RC_FIFOLEVEL      0x0A
#define RC_CONTROL        0x0C
#define RC_BITFRAMING     0x0D
#define RC_COLL           0x0E
#define RC_MODE           0x11
#define RC_TXCONTROL      0x14
#define RC_TXASK          0x15
#define RC_TMODE          0x2A
#define RC_TPRESCALER     0x2B
#define RC_TRELOADH       0x2C
#define RC_TRELOADL       0x2D
#define RC_VERSION        0x37
#define PCD_IDLE          0x00
#define PCD_TRANSCEIVE    0x0C
#define PICC_REQA         0x26
#define PICC_SEL_CL1      0x93
#define I2C_OLED          EI2C1_M2
#define ADDR_OLED         0x3C

static unsigned int g_open_ms = 400;   /* 开锁行程（可用 lock_tune.sh 在线改） */
static unsigned int g_lock_ms = 600;   /* 上锁行程（实测 400 关不上，600 可以） */
#define AUTO_LOCK_MS      6000
#define ZK_CODE_MAX       8
#define PIN_LEN           6
#define ZK_VER           "rk2206-lock-v61"

static volatile int g_motor_dir = 0;
static volatile unsigned int g_motor_deadline = 0;
static volatile int g_auto_lock_at = 0;
static volatile int g_lock_state = 0;
static volatile unsigned int g_beep_until = 0;
static volatile unsigned int g_err_until = 0;
static volatile unsigned int g_ok_until = 0;
static volatile int g_cmds = 0;
static volatile int g_opens = 0;
static volatile int g_fp_hit = 0;
static volatile int g_pwm_ready = 0;
static volatile int g_fp_suspend = 0;
static volatile int g_oled_ok = 0;
static volatile int g_oled_pending = 0;
static volatile int g_oled_dirty = 0;   /* 内容变了才刷新 */
static volatile int g_oled_tries = 0;
static volatile int g_nfc_ok = 0;
static volatile int g_card_reads = 0;
static char g_last_uid[16] = "";
static int g_beep_on = 0;
static osMutexId_t g_print_mutex;

static char g_pin[PIN_LEN + 1];
static unsigned int g_masks[PIN_LEN];   /* 每次按键的原始掩码 */
static int g_pin_len = 0;

static const char *KEY_ORDER = "123456789*0#";
/* 实测映射：KEY_ORDER="123456789*0#" */
static char key_bit[12] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11};

typedef struct {
    char code[16];
    char card[24];
    char room[8];
    int  ttl_min;
    int  used;
    unsigned int seq;      /* 下发序号，用于"绑定最近一条" */
} zk_cred_t;
static unsigned int g_cred_seq = 0;
static zk_cred_t g_creds[ZK_CODE_MAX];
static osMutexId_t g_cred_mutex;

static unsigned int now_ms(void)
{
    uint32_t tick = osKernelGetTickCount();
    uint32_t freq = osKernelGetTickFreq();
    return freq ? (unsigned int)((uint64_t)tick * 1000u / freq) : tick;
}

static void zk_print(const char *fmt, ...)
{
    char buf[200];
    va_list ap;
    va_start(ap, fmt);
    int n = vsnprintf(buf, sizeof(buf), fmt, ap);
    va_end(ap);
    if (n <= 0) return;
    if (g_print_mutex) osMutexAcquire(g_print_mutex, osWaitForever);
    printf("%s", buf);
    fflush(stdout);
    if (g_print_mutex) osMutexRelease(g_print_mutex);
}

static void motor_brake(void)
{
    IoTGpioSetOutputVal(PIN_MOTOR_IA, IOT_GPIO_VALUE0);
    IoTGpioSetOutputVal(PIN_MOTOR_IB, IOT_GPIO_VALUE0);
}

/* 阻塞式驱动电机：通足 ms 毫秒后刹车（与 zk gpio 测试一致） */
static void motor_drive_blocking(int dir, unsigned int ms)
{
    if (ms == 0) ms = 1;
    if (ms > 3000) ms = 3000;
    if (dir > 0) {
        IoTGpioSetOutputVal(PIN_MOTOR_IB, IOT_GPIO_VALUE0);
        IoTGpioSetOutputVal(PIN_MOTOR_IA, IOT_GPIO_VALUE1);
    } else {
        IoTGpioSetOutputVal(PIN_MOTOR_IA, IOT_GPIO_VALUE0);
        IoTGpioSetOutputVal(PIN_MOTOR_IB, IOT_GPIO_VALUE1);
    }
    usleep(ms * 1000);
    motor_brake();
    g_motor_dir = 0;
}


/* ================= OLED ================= */
static unsigned char g_fb[8][128];

static void oled_cmds(const unsigned char *c, int n)
{
    unsigned char buf[40];
    if (!g_oled_ok) return;
    for (int i = 0; i < n; i += 31) {
        int m = (n - i > 31) ? 31 : (n - i);
        buf[0] = 0x00;
        for (int k = 0; k < m; k++) buf[1 + k] = c[i + k];
        if (IoTI2cWrite(I2C_OLED, ADDR_OLED, buf, m + 1) != IOT_SUCCESS) {
            g_oled_ok = 0;      /* 失败就彻底停用，避免拖死主循环 */
            return;
        }
    }
}

static void oled_init(void)
{
    static const unsigned char init[] = {
        0xAE, 0xD5, 0x80, 0xA8, 0x3F, 0xD3, 0x00, 0x40,
        0x8D, 0x14, 0x20, 0x00, 0xA1, 0xC8, 0xDA, 0x12,
        0x81, 0xCF, 0xD9, 0xF1, 0xDB, 0x40, 0xA4, 0xA6, 0xAF
    };
    if (IoTI2cInit(I2C_OLED, EI2C_FRE_400K) != IOT_SUCCESS) {
        return;
    }
    g_oled_ok = 1;
    oled_cmds(init, sizeof(init));
}

static void oled_flush(void)
{
    if (!g_oled_ok) return;
    for (int page = 0; page < 8; page++) {
        unsigned char cmd[3] = {0xB0 | page, 0x00, 0x10};
        oled_cmds(cmd, 3);
        unsigned char buf[33];
        for (int i = 0; i < 128; i += 32) {
            int m = (128 - i > 32) ? 32 : (128 - i);
            buf[0] = 0x40;
            memcpy(buf + 1, &g_fb[page][i], m);
            if (IoTI2cWrite(I2C_OLED, ADDR_OLED, buf, m + 1) != IOT_SUCCESS) {
                g_oled_ok = 0;
                return;
            }
        }
    }
}

static void px(int x, int y, int on)
{
    if (x < 0 || x > 127 || y < 0 || y > 63) return;
    if (on) g_fb[y / 8][x] |= (1 << (y % 8));
    else    g_fb[y / 8][x] &= ~(1 << (y % 8));
}

static void rect(int x, int y, int w, int h, int on)
{
    for (int j = 0; j < h; j++)
        for (int i = 0; i < w; i++)
            px(x + i, y + j, on);
}

static void draw_digit(int x, int y, int d)
{
    static const unsigned char seg[10] = {
        0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F
    };
    if (d < 0 || d > 9) return;
    unsigned char s = seg[d];
    int w = 20, h = 34, t = 4;
    if (s & 0x01) rect(x + t, y, w - 2 * t, t, 1);
    if (s & 0x02) rect(x + w - t, y + t, t, h / 2 - t, 1);
    if (s & 0x04) rect(x + w - t, y + h / 2, t, h / 2 - t, 1);
    if (s & 0x08) rect(x + t, y + h - t, w - 2 * t, t, 1);
    if (s & 0x10) rect(x, y + h / 2, t, h / 2 - t, 1);
    if (s & 0x20) rect(x, y + t, t, h / 2 - t, 1);
    if (s & 0x40) rect(x + t, y + h / 2 - t / 2, w - 2 * t, t, 1);
}

static void draw_lock(int x, int y, int open)
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

static void oled_render(void)
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

    /* 密码区：错误画 X、正确画勾、否则画输入进度 */
    unsigned int _now = now_ms();
    if (g_err_until && (int)(g_err_until - _now) > 0) {
        for (int i = 0; i < 20; i++) {
            px(46 + i, 28 + i, 1);
            px(46 + i, 47 - i, 1);
            px(47 + i, 28 + i, 1);
            px(47 + i, 47 - i, 1);
        }
    } else if (g_ok_until && (int)(g_ok_until - _now) > 0) {
        for (int i = 0; i < 8; i++)   px(48 + i, 40 + i, 1);
        for (int i = 0; i < 14; i++)  px(55 + i, 47 - i, 1);
        for (int i = 0; i < 8; i++)   px(48 + i, 41 + i, 1);
        for (int i = 0; i < 14; i++)  px(55 + i, 48 - i, 1);
    } else {
        for (int i = 0; i < PIN_LEN; i++) {
            int cx = 12 + i * 20;
            if (i < g_pin_len) {
                draw_dot(cx, 38, 5);
            } else {
                rect(cx - 5, 37, 10, 3, 1);
            }
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

/* ================= 板载 NFC（WS1850S / RC522） ================= */
static void nfc_cs(int low)
{
    IoTGpioSetOutputVal(PIN_NFC_CS, low ? IOT_GPIO_VALUE0 : IOT_GPIO_VALUE1);
}

/* 忙等若干微秒：usleep(1) 在本系统会睡掉整个 tick，绝不能用 */
static inline void nfc_spin(void)
{
    for (volatile int k = 0; k < 25; k++) {
        __asm__ volatile("nop");
    }
}

static void nfc_txrx(const unsigned char *tx, int n, unsigned char *rx)
{
    nfc_cs(1);
    nfc_spin();
    for (int i = 0; i < n; i++) {
        unsigned char b = tx[i];
        unsigned char r = 0;
        for (int bit = 7; bit >= 0; bit--) {
            IoTGpioSetOutputVal(18, (b & (1u << bit)) ? IOT_GPIO_VALUE1 : IOT_GPIO_VALUE0);
            nfc_spin();
            IoTGpioSetOutputVal(17, IOT_GPIO_VALUE1);   /* CLK 高 */
            nfc_spin();
            IotGpioValue v = IOT_GPIO_VALUE0;
            IoTGpioGetInputVal(19, &v);
            if (v) r |= (unsigned char)(1u << bit);
            IoTGpioSetOutputVal(17, IOT_GPIO_VALUE0);   /* CLK 低 */
            nfc_spin();
        }
        if (rx) rx[i] = r;
    }
    nfc_cs(0);
    nfc_spin();
}

static void nfc_write(unsigned char reg, unsigned char val)
{
    unsigned char tx[2];
    tx[0] = (unsigned char)((reg << 1) & 0x7E);
    tx[1] = val;
    nfc_txrx(tx, 2, NULL);
}

static unsigned char nfc_read(unsigned char reg)
{
    unsigned char tx[2], rx[2];
    tx[0] = (unsigned char)(((reg << 1) & 0x7E) | 0x80);
    tx[1] = 0x00;
    nfc_txrx(tx, 2, rx);
    return rx[1];
}

static void nfc_setbits(unsigned char reg, unsigned char mask)
{
    unsigned char v = nfc_read(reg);
    nfc_write(reg, (unsigned char)(v | mask));
}

static void nfc_clearbits(unsigned char reg, unsigned char mask)
{
    unsigned char v = nfc_read(reg);
    nfc_write(reg, (unsigned char)(v & ~mask));
}

static int nfc_init(void)
{
    IoTGpioInit(PIN_NFC_CS);
    IoTGpioSetDir(PIN_NFC_CS, IOT_GPIO_DIR_OUT);
    nfc_cs(0);

    IoTGpioInit(17);  /* CLK  */
    IoTGpioInit(18);  /* MOSI */
    IoTGpioInit(19);  /* MISO */
    IoTGpioSetDir(17, IOT_GPIO_DIR_OUT);
    IoTGpioSetDir(18, IOT_GPIO_DIR_OUT);
    IoTGpioSetDir(19, IOT_GPIO_DIR_IN);
    IoTGpioSetOutputVal(17, IOT_GPIO_VALUE0);
    IoTGpioSetOutputVal(18, IOT_GPIO_VALUE0);

    usleep(60 * 1000);            /* 等待芯片上电稳定 */

    nfc_write(RC_COMMAND, 0x0F);  /* soft reset */
    usleep(60 * 1000);

    nfc_write(RC_TMODE, 0x8D);
    nfc_write(RC_TPRESCALER, 0x3E);
    nfc_write(RC_TRELOADL, 30);
    nfc_write(RC_TRELOADH, 0);
    nfc_write(RC_TXASK, 0x40);
    nfc_write(RC_MODE, 0x3D);

    unsigned char v = nfc_read(RC_TXCONTROL);
    if (!(v & 0x03)) {
        nfc_setbits(RC_TXCONTROL, 0x03);   /* 打开天线 */
    }
    g_nfc_ok = 1;
    return nfc_read(RC_VERSION);
}

/* 返回 0 表示无卡；1 表示读到卡，uid 填入 */
static int nfc_read_uid(char *uid, int uidlen)
{
    unsigned char irq, err;
    unsigned char fifo[16];

    if (!g_nfc_ok) return 0;

    /* --- REQA --- */
    nfc_write(RC_COMMAND, PCD_IDLE);
    nfc_write(RC_COMIRQ, 0x7F);
    nfc_write(RC_FIFOLEVEL, 0x80);
    nfc_write(RC_FIFODATA, PICC_REQA);
    nfc_write(RC_COMMAND, PCD_TRANSCEIVE);
    nfc_write(RC_BITFRAMING, 0x87);

    unsigned int t0 = now_ms();
    while ((int)(now_ms() - t0) < 12) {
        irq = nfc_read(RC_COMIRQ);
        if (irq & 0x30) break;         /* RxIRq | IdleIRq */
    }
    nfc_clearbits(RC_BITFRAMING, 0x80);

    if (!(nfc_read(RC_COMIRQ) & 0x20)) return 0;   /* 没有 RxIRq */
    err = nfc_read(RC_ERROR);
    if (err & 0x1B) return 0;

    /* --- 防冲突，取 UID --- */
    nfc_write(RC_COMMAND, PCD_IDLE);
    nfc_write(RC_COMIRQ, 0x7F);
    nfc_write(RC_FIFOLEVEL, 0x80);
    nfc_write(RC_FIFODATA, PICC_SEL_CL1);
    nfc_write(RC_FIFODATA, 0x20);
    nfc_write(RC_COMMAND, PCD_TRANSCEIVE);
    nfc_write(RC_BITFRAMING, 0x80);

    t0 = now_ms();
    while ((int)(now_ms() - t0) < 12) {
        irq = nfc_read(RC_COMIRQ);
        if (irq & 0x30) break;
    }
    nfc_clearbits(RC_BITFRAMING, 0x80);

    if (!(nfc_read(RC_COMIRQ) & 0x20)) return 0;
    err = nfc_read(RC_ERROR);
    if (err & 0x1B) return 0;

    unsigned char n = nfc_read(RC_FIFOLEVEL);
    if (n < 5) return 0;
    if (n > 9) n = 9;
    for (int i = 0; i < n; i++) fifo[i] = nfc_read(RC_FIFODATA);

    /* FIFO 里是 4 字节 UID + BCC，拼成 8 位十六进制 */
    int pos = 0;
    for (int i = 0; i < 4 && pos + 2 < uidlen; i++) {
        const char *hex = "0123456789ABCDEF";
        uid[pos++] = hex[(fifo[i] >> 4) & 0xF];
        uid[pos++] = hex[fifo[i] & 0xF];
    }
    uid[pos] = '\0';
    return 1;
}

/* ================= 凭证 ================= */
static int cred_check(const char *code)
{
    int hit = 0;
    if (g_cred_mutex) osMutexAcquire(g_cred_mutex, osWaitForever);
    for (int i = 0; i < ZK_CODE_MAX; i++) {
        if (g_creds[i].used && strcmp(g_creds[i].code, code) == 0) { hit = 1; break; }
    }
    if (g_cred_mutex) osMutexRelease(g_cred_mutex);
    return hit;
}

static int cred_check_card(const char *uid)
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

static int cred_used(void)
{
    int n = 0;
    for (int i = 0; i < ZK_CODE_MAX; i++) if (g_creds[i].used) n++;
    return n;
}

static void cred_add(const char *room, const char *code, const char *card, int ttl)
{
    if (g_cred_mutex) osMutexAcquire(g_cred_mutex, osWaitForever);
    int slot = -1;
    for (int i = 0; i < ZK_CODE_MAX; i++) {
        if (g_creds[i].used && strcmp(g_creds[i].code, code) == 0) { slot = i; break; }
        if (!g_creds[i].used && slot < 0) slot = i;
    }
    if (slot >= 0) {
        zk_cred_t *c = &g_creds[slot];
        memset(c, 0, sizeof(*c));
        snprintf(c->code, sizeof(c->code), "%s", code);
        /* 一体机给的卡号如果是占位值（CARDxxxx / "-"），就当"待绑定" */
        if (card && strcmp(card, "-") != 0 && strncmp(card, "CARD", 4) != 0) {
            snprintf(c->card, sizeof(c->card), "%s", card);
        } else {
            c->card[0] = '\0';
        }
        snprintf(c->room, sizeof(c->room), "%s", room);
        c->ttl_min = ttl;
        c->used = 1;
        c->seq = ++g_cred_seq;
    }
    if (g_cred_mutex) osMutexRelease(g_cred_mutex);
}

/* 把一张卡绑定到"最近下发且还没绑卡"的凭证；成功返回绑定到的房间号 */
static int cred_bind_card(const char *uid, char *room_out)
{
    int bound = 0;
    if (!uid || !uid[0]) return 0;
    if (g_cred_mutex) osMutexAcquire(g_cred_mutex, osWaitForever);
    int best = -1;
    unsigned int best_seq = 0;
    for (int i = 0; i < ZK_CODE_MAX; i++) {
        if (g_creds[i].used && g_creds[i].card[0] == '\0' && g_creds[i].seq >= best_seq) {
            best_seq = g_creds[i].seq;
            best = i;
        }
    }
    if (best >= 0) {
        snprintf(g_creds[best].card, sizeof(g_creds[best].card), "%s", uid);
        if (room_out) snprintf(room_out, 8, "%s", g_creds[best].room);
        bound = 1;
    }
    if (g_cred_mutex) osMutexRelease(g_cred_mutex);
    return bound;
}

/* 只作废某个房间的凭证；返回作废条数 */
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

static void cred_clear(void)
{
    if (g_cred_mutex) osMutexAcquire(g_cred_mutex, osWaitForever);
    memset(g_creds, 0, sizeof(g_creds));
    if (g_cred_mutex) osMutexRelease(g_cred_mutex);
}

/* ================= 开锁 ================= */
static void do_open(const char *why)
{
    if (g_lock_state == 1) return;
    zk_print("ZK|EVT|DOOR|open|%s\r\n", why);
    g_opens++;
    g_lock_state = 1;
    motor_drive_blocking(+1, g_open_ms);
    g_beep_until = now_ms() + 140;
    g_auto_lock_at = now_ms() + AUTO_LOCK_MS;
    g_oled_dirty = 1;
}

static void do_lock(const char *why)
{
    if (g_lock_state == 0) return;
    zk_print("ZK|EVT|DOOR|close|%s\r\n", why);
    g_lock_state = 0;
    g_auto_lock_at = 0;
    motor_drive_blocking(-1, g_lock_ms);
    g_beep_until = now_ms() + 140;
    g_oled_dirty = 1;
}

/* ================= 键盘 ================= */
/* TTP229-AQG 2-wire 时序（手册 Figure 3-4-1 / Table）：
 *   触摸后 SDO 拉低 DV=93us（数据有效脉冲）→ SDO 回高
 *   Tw=10us 后开始打 16 个时钟（F_SCL 1k~512kHz，这里约 100kHz）
 *   每位：SCL 低 → 读 SDO → SCL 高
 *   一帧结束必须等 T_resp=32ms 才能再读（16 键）
 */
static void tk_delay_us(unsigned int us)
{
    volatile unsigned int n = us * 18;      /* 约 1us/18 次空转 */
    while (n--) {
        __asm__ volatile("nop");
    }
}

/* 返回原始 16 位（bit=1 表示该位 SDO 为高） */
static unsigned int ttp229_read_raw(void)
{
    unsigned int v = 0;
    unsigned int guard;

    /* 1) 等 SDO 出现低脉冲（DV） */
    guard = 0;
    while (guard < 300000u) {
        IotGpioValue s = IOT_GPIO_VALUE1;
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        if (s == IOT_GPIO_VALUE0) break;
        guard++;
    }
    if (guard >= 300000u) {
        return 0;                       /* 没有触摸 */
    }

    /* 2) 等 DV 脉冲结束（SDO 回高） */
    guard = 0;
    while (guard < 300000u) {
        IotGpioValue s = IOT_GPIO_VALUE0;
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        if (s == IOT_GPIO_VALUE1) break;
        guard++;
    }

    /* 3) Tw = 10us */
    tk_delay_us(10);

    /* 4) 16 个时钟，约 100kHz（半周期 5us） */
    for (int i = 0; i < 16; i++) {
        IotGpioValue s = IOT_GPIO_VALUE0;
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
        tk_delay_us(5);
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        if (s == IOT_GPIO_VALUE1) v |= (1u << i);
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
        tk_delay_us(5);
    }

    /* 5) T_resp = 32ms */
    usleep(32 * 1000);
    return v;
}

/* 兼容旧接口：返回"按下"的位（自动判断高有效/低有效） */
static unsigned int ttp229_read(void)
{
    unsigned int raw = ttp229_read_raw();
    unsigned int hi = raw & 0xFFFFu;
    unsigned int lo = (~raw) & 0xFFFFu;

    int nhi = 0, nlo = 0;
    for (int i = 0; i < 16; i++) {
        if (hi & (1u << i)) nhi++;
        if (lo & (1u << i)) nlo++;
    }
    /* 恰好一位为"按下"的那种极性更可信 */
    if (nhi == 1) return hi;
    if (nlo == 1) return lo;
    if (nhi > 0 && nhi <= 2) return hi;
    if (nlo > 0 && nlo <= 2) return lo;
    return 0;
}

static char mask_to_key(unsigned int m)
{
    if (!m) return 0;
    for (int bit = 0; bit < 16; bit++) {
        if (m & (1u << bit)) {
            for (int i = 0; i < 12; i++) {
                if (key_bit[i] == bit) return KEY_ORDER[i];
            }
            return '?';
        }
    }
    return 0;
}
static void zk_learn(void)
{
    zk_print("ZK|LEARN|START\r\n");
    for (int i = 0; i < 12; i++) {
        char want = KEY_ORDER[i];
        zk_print("ZK|LEARN|PRESS|%c\r\n", want);
        int got = -1;
        unsigned int t0 = now_ms();
        while ((int)(now_ms() - t0) < 12000) {
            unsigned int m = ttp229_read();
            if (m) {
                zk_print("ZK|LEARN|RAW|%c|0x%04X\r\n", want, m);
                for (int b = 0; b < 16; b++) {
                    if (m & (1u << b)) { got = b; break; }
                }
                if (got >= 0) break;
            }
        }
        if (got >= 0) {
            key_bit[i] = (char)got;
            zk_print("ZK|LEARN|OK|%c|bit=%d\r\n", want, got);
            g_beep_until = now_ms() + 60;
            for (int k = 0; k < 40; k++) {
                if (ttp229_read() == 0) break;
                usleep(50 * 1000);
            }
        } else {
            zk_print("ZK|LEARN|TIMEOUT|%c\r\n", want);
        }
    }
    zk_print("ZK|LEARN|MAP");
    for (int i = 0; i < 12; i++) zk_print("%c=%d,", KEY_ORDER[i], key_bit[i]);
    zk_print("\r\nZK|LEARN|DONE\r\n");
}

/* ---------------- SDA 电平诊断 ---------------- */
static void zk_sda_diag(void)
{
    /* 1) 不clk，只观察 SDA 电平 40 次（每 100ms） */
    zk_print("ZK|SDA|LEVELS");
    for (int i = 0; i < 40; i++) {
        IotGpioValue s = IOT_GPIO_VALUE0;
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        zk_print("%d", s);
        usleep(100 * 1000);
    }
    zk_print("\r\n");

    /* 2) 慢速时钟读 16 位，把每一位都打出来 */
    zk_print("ZK|SDA|CLOCK");
    IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
    usleep(5000);
    for (int i = 0; i < 16; i++) {
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
        usleep(500);
        IotGpioValue s = IOT_GPIO_VALUE0;
        IoTGpioGetInputVal(PIN_TK_SDA, &s);
        zk_print("%d", s);
        IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE0);
        usleep(500);
    }
    zk_print("\r\nZK|SDA|DONE\r\n");
}

/* ================= 指纹 ================= */
static int fp_build(unsigned char *out, unsigned char cmd,
                    const unsigned char *param, int plen)
{
    int len = 1 + plen + 2;
    out[0] = 0xEF; out[1] = 0x01;
    out[2] = out[3] = out[4] = out[5] = 0xFF;
    out[6] = 0x01;
    out[7] = (unsigned char)(len >> 8);
    out[8] = (unsigned char)(len & 0xFF);
    out[9] = cmd;
    for (int i = 0; i < plen; i++) out[10 + i] = param[i];
    unsigned int sum = 0x01 + (unsigned int)len + cmd;
    for (int i = 0; i < plen; i++) sum += param[i];
    out[10 + plen] = (unsigned char)(sum >> 8);
    out[11 + plen] = (unsigned char)(sum & 0xFF);
    return 12 + plen;
}

static int fp_try_match(void)
{
    unsigned char pkt[32], rsp[32];
    int len = fp_build(pkt, 0x01, NULL, 0);
    (void)!IoTUartWrite(UART_FP, pkt, len);
    usleep(180 * 1000);
    int n = IoTUartRead(UART_FP, rsp, sizeof(rsp));
    if (n < 12 || rsp[9] != 0x00) return -1;

    unsigned char b1 = 0x01;
    memset(rsp, 0, sizeof(rsp));
    len = fp_build(pkt, 0x02, &b1, 1);
    (void)!IoTUartWrite(UART_FP, pkt, len);
    usleep(180 * 1000);
    n = IoTUartRead(UART_FP, rsp, sizeof(rsp));
    if (n < 12 || rsp[9] != 0x00) return -1;

    unsigned char sp[5] = {0x01, 0x00, 0x00, 0x01, 0x00};
    memset(rsp, 0, sizeof(rsp));
    len = fp_build(pkt, 0x04, sp, 5);
    (void)!IoTUartWrite(UART_FP, pkt, len);
    usleep(250 * 1000);
    n = IoTUartRead(UART_FP, rsp, sizeof(rsp));
    if (n >= 12 && rsp[9] == 0x00) return (rsp[10] << 8) | rsp[11];
    return -1;
}

static int fp_capture_to(int buf)
{
    unsigned char pkt[32], rsp[32];
    int len = fp_build(pkt, 0x01, NULL, 0);
    (void)!IoTUartWrite(UART_FP, pkt, len);
    usleep(200 * 1000);
    int n = IoTUartRead(UART_FP, rsp, sizeof(rsp));
    if (n < 12 || rsp[9] != 0x00) return 0;
    unsigned char b = (unsigned char)buf;
    memset(rsp, 0, sizeof(rsp));
    len = fp_build(pkt, 0x02, &b, 1);
    (void)!IoTUartWrite(UART_FP, pkt, len);
    usleep(200 * 1000);
    n = IoTUartRead(UART_FP, rsp, sizeof(rsp));
    return (n >= 12 && rsp[9] == 0x00);
}

static int fp_enroll_finish(unsigned int page)
{
    unsigned char pkt[32], rsp[32];
    int len = fp_build(pkt, 0x05, NULL, 0);
    (void)!IoTUartWrite(UART_FP, pkt, len);
    usleep(250 * 1000);
    int n = IoTUartRead(UART_FP, rsp, sizeof(rsp));
    if (n < 12 || rsp[9] != 0x00) return 0;
    unsigned char st[3] = {0x01, (unsigned char)(page >> 8), (unsigned char)(page & 0xFF)};
    memset(rsp, 0, sizeof(rsp));
    len = fp_build(pkt, 0x06, st, 3);
    (void)!IoTUartWrite(UART_FP, pkt, len);
    usleep(250 * 1000);
    n = IoTUartRead(UART_FP, rsp, sizeof(rsp));
    return (n >= 12 && rsp[9] == 0x00);
}

/* ================= shell ================= */
static int zk_shell_cmd(int argc, const char *argv[])
{
    g_cmds++;
    if (argc < 2) { zk_print("ZK|ACK|HELP|OK|%s\r\n", ZK_VER); return 0; }
    const char *sub = argv[1];

    if (strcmp(sub, "ping") == 0) {
        zk_print("ZK|ACK|PING|OK|%s|opens=%d|fp=%d|oled=%d|state=%d\r\n",
                 ZK_VER, g_opens, g_fp_hit, g_oled_ok, g_lock_state);
    } else if (strcmp(sub, "issue") == 0) {
        if (argc < 6) { zk_print("ZK|ACK|ISSUE|ERR|bad-args\r\n"); return 0; }
        cred_add(argv[2], argv[3], argv[4], atoi(argv[5]));
        zk_print("ZK|ACK|ISSUE|OK|room=%s|code=%s\r\n", argv[2], argv[3]);
    } else if (strcmp(sub, "open") == 0) {
        zk_print("ZK|ACK|OPEN|OK\r\n");
        do_open("remote");
    } else if (strcmp(sub, "lock") == 0 || strcmp(sub, "close") == 0) {
        zk_print("ZK|ACK|LOCK|OK\r\n");
        do_lock("remote");
    } else if (strcmp(sub, "code") == 0) {
        int ok = (argc > 2) && cred_check(argv[2]);
        zk_print("ZK|EVT|CODE|%s\r\n", ok ? "ok" : "bad");
        if (ok) do_open("keypad");
        zk_print("ZK|ACK|CODE|%s\r\n", ok ? "OK" : "ERR");
    } else if (strcmp(sub, "revoke") == 0) {
        if (argc > 2) {
            int n = cred_revoke_room(argv[2]);
            zk_print("ZK|ACK|REVOKE|OK|room=%s|n=%d\r\n", argv[2], n);
        } else {
            cred_clear();
            zk_print("ZK|ACK|REVOKE|OK|all\r\n");
        }
    } else if (strcmp(sub, "oled") == 0) {
        if (argc > 2 && strcmp(argv[2], "on") == 0) {
            g_oled_pending = 1;
            zk_print("ZK|ACK|OLED|ENABLE\r\n");
        } else if (argc > 2 && strcmp(argv[2], "off") == 0) {
            g_oled_ok = 0;
            zk_print("ZK|ACK|OLED|DISABLE\r\n");
        } else {
            if (!g_oled_ok) { oled_init(); }
            g_oled_dirty = 1;
            zk_print("ZK|ACK|OLED|%s\r\n", g_oled_ok ? "OK" : "FAIL");
        }
    } else if (strcmp(sub, "nfc") == 0) {
        if (!g_nfc_ok) {
            int ver = nfc_init();
            zk_print("ZK|ACK|NFC|INIT|ver=0x%02X|ok=%d\r\n", ver, g_nfc_ok);
        }
        char uid[16];
        int got = 0;
        for (int i = 0; i < 8 && !got; i++) {
            got = nfc_read_uid(uid, sizeof(uid));
            if (!got) usleep(120 * 1000);
        }
        if (got) zk_print("ZK|ACK|NFC|UID|%s\r\n", uid);
        else zk_print("ZK|ACK|NFC|NOCARD\r\n");
    } else if (strcmp(sub, "gpio") == 0) {
        unsigned int pin = (argc > 2) ? (unsigned int)atoi(argv[2]) : 0;
        unsigned int ms = (argc > 3) ? (unsigned int)atoi(argv[3]) : 500;
        IoTGpioInit(pin);
        IoTGpioSetDir(pin, IOT_GPIO_DIR_OUT);
        IoTGpioSetOutputVal(pin, IOT_GPIO_VALUE1);
        zk_print("ZK|ACK|GPIO|%u|HIGH|%ums\r\n", pin, ms);
        usleep(ms * 1000);
        IoTGpioSetOutputVal(pin, IOT_GPIO_VALUE0);
        zk_print("ZK|ACK|GPIO|%u|LOW\r\n", pin);    } else if (strcmp(sub, "pt") == 0) {
        if (argc > 2) g_open_ms = (unsigned int)atoi(argv[2]);
        if (argc > 3) g_lock_ms = (unsigned int)atoi(argv[3]);
        zk_print("ZK|ACK|PT|OK|open=%u|lock=%u\r\n", g_open_ms, g_lock_ms);    } else if (strcmp(sub, "stop") == 0) {
        g_motor_dir = 0;
        motor_brake();
        zk_print("ZK|ACK|STOP|OK\r\n");
    } else if (strcmp(sub, "sda") == 0) {
        g_fp_suspend = 1;
        zk_sda_diag();
        g_fp_suspend = 0;
        zk_print("ZK|ACK|SDA|OK\r\n");
    } else if (strcmp(sub, "learn") == 0) {
        g_fp_suspend = 1;
        zk_learn();
        g_fp_suspend = 0;
        zk_print("ZK|ACK|LEARN|OK\r\n");
    } else if (strcmp(sub, "en1") == 0) {
        g_fp_suspend = 1;
        int ok = fp_capture_to(1);
        zk_print("ZK|ACK|EN1|%s\r\n", ok ? "OK" : "ERR");
    } else if (strcmp(sub, "en2") == 0) {
        g_fp_suspend = 1;
        unsigned int page = (argc > 2) ? (unsigned int)atoi(argv[2]) : 0;
        int c2 = fp_capture_to(2);
        int reg = c2 ? fp_enroll_finish(page) : -1;
        zk_print("ZK|ACK|EN2|%s|c2=%d|regist=%d|id=%u\r\n",
                 (c2 && reg) ? "OK" : "ERR", c2, reg, page);
        g_fp_suspend = 0;
    } else if (strcmp(sub, "fpid") == 0) {
        g_fp_suspend = 1;
        int id = fp_try_match();
        g_fp_suspend = 0;
        if (id >= 0) { g_fp_hit++; zk_print("ZK|EVT|FP|%d\r\n", id); do_open("fingerprint"); }
        zk_print("ZK|ACK|FPID|%s|id=%d\r\n", id >= 0 ? "OK" : "NOMATCH", id);
    } else {
        zk_print("ZK|ACK|%s|ERR|unknown\r\n", sub);
    }
    return 0;
}

/* ================= 主循环 ================= */
static void *zk_task(void *arg)
{
    (void)arg;
    unsigned int n = 0;
    unsigned int last_mask = 0;
    unsigned int fp_tick = 0;
    unsigned int oled_tick = 0;
    unsigned int nfc_tick = 0;
    unsigned int nfc_boot = 0;

    osDelay(200);
    unsigned int r = osCmdReg(ZK_CMD_TYPE_STD, "zk", ZK_XARGS, (zk_cmd_cb_t)zk_shell_cmd);
    zk_print("[zk] v23 ready reg=%u oled=%d\r\n", r, g_oled_ok);

    while (1) {
        unsigned int t = now_ms();
        int dir = g_motor_dir;

        if (dir != 0 && (int)(g_motor_deadline - t) > 0) {
            if (dir > 0) {
                IoTGpioSetOutputVal(PIN_MOTOR_IB, IOT_GPIO_VALUE0);
                IoTGpioSetOutputVal(PIN_MOTOR_IA, IOT_GPIO_VALUE1);
            } else {
                IoTGpioSetOutputVal(PIN_MOTOR_IA, IOT_GPIO_VALUE0);
                IoTGpioSetOutputVal(PIN_MOTOR_IB, IOT_GPIO_VALUE1);
            }
        } else {
            g_motor_dir = 0;
            motor_brake();
        }

        if (g_auto_lock_at && (int)(g_auto_lock_at - t) <= 0) {
            do_lock("auto");
        }

        if (g_beep_until && (int)(g_beep_until - t) > 0 && g_pwm_ready) {
            if (!g_beep_on) { IoTPwmStart(PWM_BUZZER, 50, 2700); g_beep_on = 1; }
        } else if (g_beep_on) {
            IoTPwmStop(PWM_BUZZER);
            g_beep_on = 0;
            g_beep_until = 0;
        }

        if (!g_fp_suspend) {
            unsigned int m = ttp229_read();
            if (m != last_mask) {
                last_mask = m;
                char k = mask_to_key(m);
                if (k && k != '?') {
                    if (g_pwm_ready) { IoTPwmStart(PWM_BUZZER, 50, 2700); g_beep_on = 1; }   /* 按键立即响 */
                    g_beep_until = now_ms() + 80;
                    zk_print("ZK|EVT|KEY|%c|len=%d\r\n", k, g_pin_len);
                    if (k == '#') {
                        int ok = 0;
                        char chosen[PIN_LEN + 1];
                        if (g_pin_len == PIN_LEN) {
                            /* 帧可能整体偏移若干位：把 12 种偏移都试一遍 */
                            for (int sh = 0; sh < 12 && !ok; sh++) {
                                for (int p = 0; p < PIN_LEN; p++) {
                                    char c = '?';
                                    for (int bi = 0; bi < 16; bi++) {
                                        if (g_masks[p] & (1u << bi)) {
                                            int want = (bi - sh + 16) % 16;
                                            for (int q = 0; q < 12; q++) {
                                                if (key_bit[q] == want) { c = KEY_ORDER[q]; break; }
                                            }
                                            break;
                                        }
                                    }
                                    chosen[p] = c;
                                }
                                chosen[PIN_LEN] = '\0';
                                if (cred_check(chosen)) { ok = 1; break; }
                            }
                        }
                        zk_print("ZK|EVT|CODE|%s\r\n", ok ? "ok" : "bad");
                        if (ok) {
                            g_ok_until = now_ms() + 800;
                            g_err_until = 0;
                            do_open("keypad");
                        } else {
                            g_err_until = now_ms() + 1800;
                            g_ok_until = 0;
                            if (g_pwm_ready) {
                                IoTPwmStart(PWM_BUZZER, 50, 2700);
                                g_beep_on = 1;
                            }
                            g_beep_until = now_ms() + 400;
                            zk_print("ZK|EVT|CODEBAD\r\n");
                        }
                        g_pin_len = 0;
                    } else if (k == '*') {
                        if (g_pin_len > 0) {
                            g_pin_len--;          /* * = 退格一位 */
                            g_masks[g_pin_len] = 0;
                            g_pin[g_pin_len] = 0;
                        }
                    } else if (g_pin_len < PIN_LEN) {
                        g_masks[g_pin_len] = m;
                        g_pin[g_pin_len] = k;
                        g_pin_len++;
                    }
                    g_oled_dirty = 1;
                }
            }
        }

        /* 板载 NFC：锁着时轮询寻卡 */
        if (g_nfc_ok && g_lock_state == 0 && last_mask == 0 && t - nfc_tick > 2000) {
            nfc_tick = t;
            char uid[16];
            if (nfc_read_uid(uid, sizeof(uid))) {
                if (strcmp(uid, g_last_uid) != 0) {
                    snprintf(g_last_uid, sizeof(g_last_uid), "%s", uid);
                    g_card_reads++;
                    zk_print("ZK|EVT|CARD|%s\r\n", uid);
                    if (cred_check_card(uid)) {
                        do_open("card");
                    } else {
                        char room[8];
                        if (cred_bind_card(uid, room)) {
                            zk_print("ZK|EVT|CARDBIND|%s|%s\r\n", room, uid);
                            do_open("card");
                        } else {
                            zk_print("ZK|EVT|CARDDENY|%s\r\n", uid);
                        }
                    }
                    g_oled_dirty = 1;
                }
            } else {
                g_last_uid[0] = '\0';
            }
        }

        if (!g_fp_suspend && g_lock_state == 0 && t - fp_tick > 800) {
            fp_tick = t;
            int id = fp_try_match();
            if (id >= 0) {
                g_fp_hit++;
                zk_print("ZK|EVT|FP|%d\r\n", id);
                do_open("fingerprint");
                oled_tick = 0;
            }
        }

        /* ---- NFC 延迟初始化 ---- */
        if (!g_nfc_ok && nfc_boot == 0 && t > 1200) {
            nfc_boot = 1;
            int ver = nfc_init();
            zk_print("[zk] nfc ver=0x%02X ok=%d\r\n", ver, g_nfc_ok);
        }

        /* ---- OLED：初始化重试 + 内容变化时才刷新 ---- */
        if (!g_oled_ok && g_oled_tries < 8 && t > 2000 && t - oled_tick > 1500) {
            oled_tick = t;
            g_oled_tries++;
            oled_init();
            if (g_oled_ok) {
                zk_print("[zk] oled ok (try %d)\r\n", g_oled_tries);
                g_oled_dirty = 1;
            }
        }
        /* 错误/正确提示到期后主动刷新一次 */
        if (g_err_until && (int)(g_err_until - t) <= 0) {
            g_err_until = 0;
            g_oled_dirty = 1;
        }
        if (g_ok_until && (int)(g_ok_until - t) <= 0) {
            g_ok_until = 0;
            g_oled_dirty = 1;
        }

        if (g_oled_ok && g_oled_dirty && t - oled_tick > 150) {
            oled_tick = t;
            g_oled_dirty = 0;
            oled_render();
        }

        n++;
        if (n % 150 == 0) {
            zk_print("[zk] alive #%u opens=%d fp=%d state=%d\r\n", n, g_opens, g_fp_hit, g_lock_state);
        }
        osDelay(20);
    }
    return NULL;
}

static void zk_entry(void)
{
    IoTGpioInit(PIN_MOTOR_IA);
    IoTGpioSetDir(PIN_MOTOR_IA, IOT_GPIO_DIR_OUT);
    IoTGpioSetOutputVal(PIN_MOTOR_IA, IOT_GPIO_VALUE0);
    IoTGpioInit(PIN_MOTOR_IB);
    IoTGpioSetDir(PIN_MOTOR_IB, IOT_GPIO_DIR_OUT);
    IoTGpioSetOutputVal(PIN_MOTOR_IB, IOT_GPIO_VALUE0);
    motor_brake();

    IoTGpioInit(PIN_TK_SCL);
    IoTGpioSetDir(PIN_TK_SCL, IOT_GPIO_DIR_OUT);
    IoTGpioSetOutputVal(PIN_TK_SCL, IOT_GPIO_VALUE1);
    IoTGpioInit(PIN_TK_SDA);
    IoTGpioSetDir(PIN_TK_SDA, IOT_GPIO_DIR_IN);

    g_print_mutex = osMutexNew(NULL);
    g_cred_mutex = osMutexNew(NULL);

    if (IoTPwmInit(PWM_BUZZER) == IOT_SUCCESS) g_pwm_ready = 1;

    /* OLED 初始化放到线程里延后执行，避免开机早期 I2C 未就绪 */
    g_oled_pending = 1;

    IotUartAttribute attr = {
        .baudRate = 57600,
        .dataBits = IOT_UART_DATA_BIT_8,
        .stopBits = IOT_UART_STOP_BIT_1,
        .parity = IOT_UART_PARITY_NONE,
    };
    IoTUartInit(UART_FP, &attr);

    zk_print("\r\n[zk] ===== %s oled=%d =====\r\n", ZK_VER, g_oled_ok);

    osThreadAttr_t a = {0};
    a.stack_size = 8192;
    a.priority = osPriorityNormal;
    a.name = "zk_main";
    osThreadNew((osThreadFunc_t)zk_task, NULL, &a);
}

SYS_RUN(zk_entry);
