/*
 * 芯宿·智控 —— 智能家居板固件 v7
 * LCD 仪表盘 + 全部传感器 + 外设控制（硬件 SPI 驱动 LCD）
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

#define ZH_VER           "rk2206-home-v7"

static osMutexId_t g_print_mutex;
static int inited_i2c = 0, inited_adc = 0, inited_pwm = 0, inited_lcd = 0, inited_gpio = 0;
static float g_temp = -100.0f, g_hum = -100.0f;
static int g_lux = -1, g_gas = 0, g_pir = 0, g_led_on = 0, g_auto = 1;

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

static void ensure_i2c(void) { if (!inited_i2c) { inited_i2c = 1; IoTI2cInit(I2C_ENV, EI2C_FRE_100K); } }
static void ensure_adc(void) { if (!inited_adc) { inited_adc = 1; IoTAdcInit(ADC_GAS); } }

static void ensure_pwm(void)
{
    if (inited_pwm) return;
    inited_pwm = 1;
    IoTPwmInit(PWM_R); IoTPwmInit(PWM_G); IoTPwmInit(PWM_B);
    IoTPwmInit(PWM_BEEP); IoTPwmInit(PWM_MOTOR);
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

/* ---------------- LCD 仪表盘 ---------------- */
static void dash_static(void)
{
    lcd_fill(0, 0, LCD_W, LCD_H, LCD_WHITE);
    lcd_show_chinese(8, 4, "芯宿智控", LCD_BLUE, LCD_WHITE, 24, 0);
    lcd_show_string(160, 12, "ROOM ENV", LCD_GRAY, LCD_WHITE, 16, 0);
    lcd_draw_line(0, 36, LCD_W, 36, LCD_BLUE);

    lcd_show_chinese(8, 50, "温度", LCD_BLACK, LCD_WHITE, 24, 0);
    lcd_show_chinese(8, 90, "湿度", LCD_BLACK, LCD_WHITE, 24, 0);
    lcd_show_chinese(8, 130, "光照", LCD_BLACK, LCD_WHITE, 24, 0);
    lcd_draw_line(0, 170, LCD_W, 170, LCD_GRAY);

    lcd_show_chinese(8, 182, "人体", LCD_BLACK, LCD_WHITE, 24, 0);
    lcd_show_chinese(168, 182, "燃气", LCD_BLACK, LCD_WHITE, 24, 0);
}

static void dash_values(void)
{
    lcd_fill(80, 46, 310, 86, LCD_WHITE);
    lcd_show_float_num1(80, 50, g_temp, 4, LCD_RED, LCD_WHITE, 24);
    lcd_show_string(250, 50, "C", LCD_RED, LCD_WHITE, 24, 0);

    lcd_fill(80, 86, 310, 126, LCD_WHITE);
    lcd_show_float_num1(80, 90, g_hum, 4, LCD_BLUE, LCD_WHITE, 24);
    lcd_show_string(250, 90, "%", LCD_BLUE, LCD_WHITE, 24, 0);

    lcd_fill(80, 126, 310, 166, LCD_WHITE);
    lcd_show_int_num(80, 130, (uint16_t)g_lux, 5, LCD_YELLOW, LCD_WHITE, 24);
    lcd_show_string(250, 130, "lx", LCD_YELLOW, LCD_WHITE, 16, 0);

    lcd_fill(60, 178, 160, 214, LCD_WHITE);
    if (g_pir) lcd_show_chinese(60, 182, "有人", LCD_RED, LCD_WHITE, 24, 0);
    else       lcd_show_chinese(60, 182, "无人", LCD_GRAY, LCD_WHITE, 24, 0);

    lcd_fill(220, 178, 318, 214, LCD_WHITE);
    if (g_gas > 2500) lcd_show_chinese(220, 182, "报警", LCD_RED, LCD_WHITE, 24, 0);
    else              lcd_show_chinese(220, 182, "正常", LCD_GREEN, LCD_WHITE, 24, 0);

    lcd_fill(0, 216, LCD_W, 240, LCD_WHITE);
    char buf[32];
    snprintf(buf, sizeof(buf), "gas %d   light %d%%", g_gas, g_led_on ? 1 : 0);
    lcd_show_string(8, 218, (const uint8_t *)buf, LCD_GRAY, LCD_WHITE, 16, 0);
}

/* ---------------- shell ---------------- */
static int zh_shell_cmd(int argc, const char **argv)
{
    if (argc < 2) { zh_print("ZH|ACK|HELP|OK|%s\r\n", ZH_VER); return 0; }
    const char *sub = argv[1];

    if (strcmp(sub, "ping") == 0) {
        zh_print("ZH|ACK|PING|OK|%s|i2c=%d|adc=%d|pwm=%d|lcd=%d\r\n",
                 ZH_VER, inited_i2c, inited_adc, inited_pwm, inited_lcd);
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
    } else if (strcmp(sub, "lcd") == 0) {
        unsigned int r = lcd_init();
        inited_lcd = (r == 0) ? 1 : 0;
        zh_print("ZH|ACK|LCD|init=%u\r\n", r);
        if (inited_lcd) { dash_static(); dash_values(); zh_print("ZH|ACK|LCD|drawn\r\n"); }
    } else if (strcmp(sub, "auto") == 0) {
        if (argc > 2) g_auto = atoi(argv[2]) ? 1 : 0;
        zh_print("ZH|ACK|AUTO|%d\r\n", g_auto);
    } else {
        zh_print("ZH|ACK|%s|ERR\r\n", sub);
    }
    return 0;
}

/* ---------------- 主循环 ---------------- */
static void *zh_task(void *arg)
{
    (void)arg;
    unsigned int n = 0;
    int last_pir = -1;

    osDelay(800);
    unsigned int reg = osCmdReg(ZH_CMD_TYPE_STD, "zh", ZH_XARGS, (zh_cmd_cb_t)zh_shell_cmd);
    zh_print("[zh] %s ready reg=%u\r\n", ZH_VER, reg);

    /* LCD 初始化（失败也不影响其它功能） */
    if (lcd_init() == 0) {
        inited_lcd = 1;
        dash_static();
        zh_print("[zh] lcd ok\r\n");
    } else {
        zh_print("[zh] lcd failed\r\n");
    }

    while (1) {
        ensure_gpio();
        int p = 0;
        IotGpioValue v = IOT_GPIO_VALUE0;
        IoTGpioGetInputVal(PIN_PIR, &v);
        p = (v == IOT_GPIO_VALUE1);
        if (p != last_pir) {
            last_pir = p;
            g_pir = p;
            zh_print("ZH|EVT|PIR|%d\r\n", p);
            if (p && g_auto) rgb_set(100, 80, 40);
        }

        /* 每 4 秒读一次传感器并刷新仪表盘 */
        if (n % 8 == 0) {
            ensure_i2c();
            ensure_adc();
            sht30_read();
            bh1750_read();
            unsigned short gv = 0;
            IoTAdcGetVal(ADC_GAS, &gv);
            g_gas = gv;
            if (inited_lcd) dash_values();
        }

        n++;
        if (n % 20 == 0) zh_print("[zh] alive #%u t=%.1f h=%.1f lux=%d gas=%d\r\n",
                                  n, g_temp, g_hum, g_lux, g_gas);
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
