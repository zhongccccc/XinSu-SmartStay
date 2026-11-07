/*
 * 芯宿·智控 —— 智能家居板固件 v4（按需初始化版）
 *
 * 关键改动：所有外设初始化都延迟到命令里执行，避免开机时某个外设把系统搞挂。
 * 命令：
 *   zh ping / zh i2c / zh adc / zh pwm / zh lcd / zh env
 *   zh rgb r g b / zh rgboff / zh beep ms / zh pir / zh gas / zh motor dir ms
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
#include "iot_adc.h"
#include "iot_errno.h"
#include "lcd.h"

#define ZH_CMD_TYPE_STD   1
#define ZH_XARGS          0xFFFFFFFFu
typedef unsigned int (*zh_cmd_cb_t)(unsigned int argc, const char **argv);
extern unsigned int osCmdReg(int cmdType, const char *cmdKey,
                             unsigned int paraNum, zh_cmd_cb_t cmdProc);

#define I2C_ENV          EI2C0_M2
#define ADDR_SHT30       0x44
#define ADDR_BH1750      0x23

#define PWM_R            EPWMDEV_PWM1_M1
#define PWM_G            EPWMDEV_PWM7_M1
#define PWM_B            EPWMDEV_PWM0_M1
#define PWM_BEEP         EPWMDEV_PWM5_M0
#define PWM_MOTOR        EPWMDEV_PWM6_M0

#define PIN_PIR          3
#define PIN_LED          5
#define ADC_GAS          4

#define ZH_VER           "rk2206-home-v6"

static osMutexId_t g_print_mutex;
static int inited_i2c = 0, inited_adc = 0, inited_pwm = 0, inited_lcd = 0, inited_gpio = 0;
static float g_temp = -100.0f, g_hum = -100.0f;
static int g_lux = -1, g_gas = 0, g_pir = 0, g_led_on = 0;

static void zh_print(const char *fmt, ...)
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

static void ensure_gpio(void)
{
    if (inited_gpio) return;
    inited_gpio = 1;
    IoTGpioInit(PIN_PIR);
    IoTGpioSetDir(PIN_PIR, IOT_GPIO_DIR_IN);
    IoTGpioInit(PIN_LED);
    IoTGpioSetDir(PIN_LED, IOT_GPIO_DIR_OUT);
    IoTGpioSetOutputVal(PIN_LED, IOT_GPIO_VALUE0);
}

static void ensure_i2c(void)
{
    if (inited_i2c) return;
    inited_i2c = 1;
    IoTI2cInit(I2C_ENV, EI2C_FRE_100K);
}

static void ensure_adc(void)
{
    if (inited_adc) return;
    inited_adc = 1;
    IoTAdcInit(ADC_GAS);
}

static void ensure_pwm(void)
{
    if (inited_pwm) return;
    inited_pwm = 1;
    IoTPwmInit(PWM_R);
    IoTPwmInit(PWM_G);
    IoTPwmInit(PWM_B);
    IoTPwmInit(PWM_BEEP);
    IoTPwmInit(PWM_MOTOR);
}

static int sht30_read(void)
{
    unsigned char cmd[2] = {0x2C, 0x06};
    unsigned char buf[6];
    if (IoTI2cWrite(I2C_ENV, ADDR_SHT30, cmd, 2) != IOT_SUCCESS) return 0;
    usleep(20 * 1000);
    if (IoTI2cRead(I2C_ENV, ADDR_SHT30, buf, 6) != IOT_SUCCESS) return 0;
    int traw = (buf[0] << 8) | buf[1];
    int hraw = (buf[3] << 8) | buf[4];
    g_temp = -45.0f + 175.0f * (float)traw / 65535.0f;
    g_hum = 100.0f * (float)hraw / 65535.0f;
    return 1;
}

static int bh1750_read(void)
{
    unsigned char cmd = 0x10;
    unsigned char buf[2];
    IoTI2cWrite(I2C_ENV, ADDR_BH1750, &cmd, 1);
    usleep(180 * 1000);
    if (IoTI2cRead(I2C_ENV, ADDR_BH1750, buf, 2) != IOT_SUCCESS) return 0;
    g_lux = (int)(((buf[0] << 8) | buf[1]) / 1.2f);
    return 1;
}

static void rgb_set(int r, int g, int b)
{
    ensure_pwm();
    if (r) IoTPwmStart(PWM_R, (unsigned short)r, 1000); else IoTPwmStop(PWM_R);
    if (g) IoTPwmStart(PWM_G, (unsigned short)g, 1000); else IoTPwmStop(PWM_G);
    if (b) IoTPwmStart(PWM_B, (unsigned short)b, 1000); else IoTPwmStop(PWM_B);
    g_led_on = (r || g || b);
}

static int zh_shell_cmd(int argc, const char **argv)
{
    if (argc < 2) { zh_print("ZH|ACK|HELP|OK|%s\r\n", ZH_VER); return 0; }
    const char *sub = argv[1];

    if (strcmp(sub, "ping") == 0) {
        zh_print("ZH|ACK|PING|OK|%s|i2c=%d|adc=%d|pwm=%d|lcd=%d\r\n",
                 ZH_VER, inited_i2c, inited_adc, inited_pwm, inited_lcd);
    } else if (strcmp(sub, "i2c") == 0) {
        ensure_i2c();
        zh_print("ZH|ACK|I2C|OK\r\n");
    } else if (strcmp(sub, "adc") == 0) {
        ensure_adc();
        unsigned short v = 0;
        IoTAdcGetVal(ADC_GAS, &v);
        g_gas = v;
        zh_print("ZH|ACK|ADC|%u\r\n", v);
    } else if (strcmp(sub, "pwm") == 0) {
        ensure_pwm();
        zh_print("ZH|ACK|PWM|OK\r\n");
    } else if (strcmp(sub, "lcd") == 0) {
        zh_print("ZH|ACK|LCD|begin\r\n");
        unsigned int r = lcd_init();
        inited_lcd = (r == 0) ? 1 : 0;
        zh_print("ZH|ACK|LCD|init=%u\r\n", r);
        if (inited_lcd) {
            lcd_fill(0, 0, LCD_W, LCD_H, LCD_RED);
            lcd_show_string(20, 100, "LCD OK", LCD_WHITE, LCD_RED, 24, 0);
            zh_print("ZH|ACK|LCD|drawn\r\n");
        }
    } else if (strcmp(sub, "env") == 0) {
        ensure_i2c();
        int a = sht30_read();
        int b = bh1750_read();
        zh_print("ZH|ACK|ENV|%s|t=%.1f|h=%.1f|lux=%d\r\n",
                 (a && b) ? "OK" : "PART", g_temp, g_hum, g_lux);
    } else if (strcmp(sub, "rgb") == 0) {
        int r = (argc > 2) ? atoi(argv[2]) : 0;
        int g = (argc > 3) ? atoi(argv[3]) : 0;
        int b = (argc > 4) ? atoi(argv[4]) : 0;
        rgb_set(r, g, b);
        zh_print("ZH|ACK|RGB|OK|%d,%d,%d\r\n", r, g, b);
    } else if (strcmp(sub, "rgboff") == 0) {
        rgb_set(0, 0, 0);
        zh_print("ZH|ACK|RGB|OFF\r\n");
    } else if (strcmp(sub, "beep") == 0) {
        ensure_pwm();
        int ms = (argc > 2) ? atoi(argv[2]) : 100;
        IoTPwmStart(PWM_BEEP, 50, 2700);
        usleep(ms * 1000);
        IoTPwmStop(PWM_BEEP);
        zh_print("ZH|ACK|BEEP|OK\r\n");
    } else if (strcmp(sub, "pir") == 0) {
        ensure_gpio();
        IotGpioValue v = IOT_GPIO_VALUE0;
        IoTGpioGetInputVal(PIN_PIR, &v);
        g_pir = (v == IOT_GPIO_VALUE1);
        zh_print("ZH|ACK|PIR|%d\r\n", g_pir);
    } else if (strcmp(sub, "gas") == 0) {
        ensure_adc();
        unsigned short v = 0;
        IoTAdcGetVal(ADC_GAS, &v);
        g_gas = v;
        zh_print("ZH|ACK|GAS|%u\r\n", v);
    } else {
        zh_print("ZH|ACK|%s|ERR\r\n", sub);
    }
    return 0;
}

static void *zh_task(void *arg)
{
    (void)arg;
    unsigned int n = 0;
    osDelay(500);
    unsigned int reg = osCmdReg(ZH_CMD_TYPE_STD, "zh", ZH_XARGS, (zh_cmd_cb_t)zh_shell_cmd);
    zh_print("[zh] %s ready reg=%u\r\n", ZH_VER, reg);
    while (1) {
        n++;
        if (n % 10 == 0) zh_print("[zh] alive #%u\r\n", n);
        osDelay(500);
    }
    return NULL;
}

static void zh_entry(void)
{
    g_print_mutex = osMutexNew(NULL);
    zh_print("\r\n[zh] entry %s\r\n", ZH_VER);



    osThreadAttr_t a = {0};
    a.stack_size = 8192;
    a.priority = osPriorityNormal;
    a.name = "zh_main";
    osThreadNew((osThreadFunc_t)zh_task, NULL, &a);
}

SYS_RUN(zh_entry);
