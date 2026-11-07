# -*- coding: utf-8 -*-
"""v44：接入板载 NFC（WS1850S/RC522，SPI0_M1）→ 刷卡开门。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

# 1) 头文件
s = s.replace('#include "iot_uart.h"', '#include "iot_uart.h"\n#include "iot_spi.h"', 1)

# 2) 常量
s = s.replace('#define UART_FP           1',
'''#define UART_FP           1
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
#define PICC_SEL_CL1      0x93''', 1)

# 3) 全局
s = s.replace('static volatile int g_oled_tries = 0;',
              'static volatile int g_oled_tries = 0;\n'
              'static volatile int g_nfc_ok = 0;\n'
              'static volatile int g_card_reads = 0;\n'
              'static char g_last_uid[16] = "";', 1)

# 4) NFC 驱动代码，插到 "/* ================= 凭证 ================= */" 之前
anchor = "/* ================= 凭证 ================= */"
NFC = r'''/* ================= 板载 NFC（WS1850S / RC522） ================= */
static void nfc_cs(int low)
{
    IoTGpioSetOutputVal(PIN_NFC_CS, low ? IOT_GPIO_VALUE0 : IOT_GPIO_VALUE1);
}

static void nfc_txrx(const unsigned char *tx, int n, unsigned char *rx)
{
    IoT_SPI_InitTypeDef cfg = {0};
    (void)cfg;
    nfc_cs(1);
    for (int i = 0; i < n; i++) {
        unsigned char b = tx[i];
        unsigned char r = 0;
        for (int bit = 7; bit >= 0; bit--) {
            IoTGpioSetOutputVal(18, (b & (1u << bit)) ? IOT_GPIO_VALUE1 : IOT_GPIO_VALUE0);
            usleep(1);
            IoTGpioSetOutputVal(17, IOT_GPIO_VALUE1);   /* CLK 高 */
            usleep(1);
            IotGpioValue v = IOT_GPIO_VALUE0;
            IoTGpioGetInputVal(19, &v);
            if (v) r |= (unsigned char)(1u << bit);
            IoTGpioSetOutputVal(17, IOT_GPIO_VALUE0);   /* CLK 低 */
            usleep(1);
        }
        if (rx) rx[i] = r;
    }
    nfc_cs(0);
    usleep(5);
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
    while ((int)(now_ms() - t0) < 30) {
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
    while ((int)(now_ms() - t0) < 30) {
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

'''
assert anchor in s
s = s.replace(anchor, NFC + anchor, 1)

s = s.replace("rk2206-lock-v43", "rk2206-lock-v44")
open(P, "w", encoding="utf-8").write(s)
print("patched v44 nfc driver")
