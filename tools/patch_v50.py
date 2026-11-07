# -*- coding: utf-8 -*-
"""v50：NFC 的 SPI 改忙等（不再 usleep），轮询降频，按键时暂停轮询。"""
P = r"E:\zhikong\board_app\zk_lock.c"
s = open(P, encoding="utf-8").read()

old = '''static void nfc_txrx(const unsigned char *tx, int n, unsigned char *rx)
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
}'''

new = '''/* 忙等若干微秒：usleep(1) 在本系统会睡掉整个 tick，绝不能用 */
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
}'''
assert old in s
s = s.replace(old, new, 1)

# 轮询降频到 2 秒，且键盘有按下时跳过
s = s.replace('if (g_nfc_ok && g_lock_state == 0 && t - nfc_tick > 1200) {',
              'if (g_nfc_ok && g_lock_state == 0 && last_mask == 0 && t - nfc_tick > 2000) {', 1)

s = s.replace("rk2206-lock-v49", "rk2206-lock-v50")
open(P, "w", encoding="utf-8").write(s)
print("patched v50")
