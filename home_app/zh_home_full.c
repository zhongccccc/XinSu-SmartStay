/*
 * 芯宿·智控 —— 智能家居板固件（通晓 RK2206 开发板）
 *
 * 通过 shell 子命令 "zh" 暴露外设，供一体机调用：
 *   zh ping                      握手
 *   zh env                       温湿度 + 光照
 *   zh rgb <r> <g> <b>           0-100 三色
 *   zh rgboff                    关灯
 *   zh beep <ms>                 蜂鸣器
 *   zh motor <1|-1> <ms>         电机正反
 *   zh pir                       当前是否有人
 *   zh gas                       燃气 ADC 原始值
 *
 * 自动联动：检测到人 → 自动开灯；燃气超阈值 → 报警事件
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

/* ---- 引脚（来自厂商例程）---- */
#define I2C_ENV          EI2C0_M2
#define ADDR_SHT30       0x44
#define ADDR_BH1750      0x23
#define ADDR_MPU6050     0x68

#define PWM_R            EPWMDEV_PWM1_M1
#define PWM_G            EPWMDEV_PWM7_M1
#define PWM_B            EPWMDEV_PWM0_M1
#define PWM_BEEP         EPWMDEV_PWM5_M0
#define PWM_MOTOR        EPWMDEV_PWM6_M0

#define PIN_PIR          3      /* GPIO0_PA3 */
#define PIN_LED          5      /* GPIO0_PA5 */
#define ADC_GAS          4
#define ADC_KEY          7

#define ZH_VER           "rk2206-home-v3"

static osMutexId_t g_print_mutex;
static volatile int g_pwm_ok = 0;
static volatile int g_led_on = 0;
static volatile int g_pir = 0;
static volatile int g_gas = 0;
static volatile int g_auto_light = 1;   /* 有人自动开灯 */
static volatile int g_lcd_ok = 0;
static float g_temp = -100.0f, g_hum = -100.0f;
static int g_lux = -1;

typedef struct {
    char code[16];
} dummy_t;

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

/* ---------------- RGB ---------------- */
static void rgb_set(int r, int g, int b)
{
    if (!g_pwm_ok) return;
    if (r < 0) r = 0;
    if (r > 100) r = 100;
    if (g < 0) g = 0;
    if (g > 100) g = 100;
    if (b < 0) b = 0;
    if (b > 100) b = 100;
    if (r) IoTPwmStart(PWM_R, (unsigned short)r, 1000); else IoTPwmStop(PWM_R);
    if (g) IoTPwmStart(PWM_G, (unsigned short)g, 1000); else IoTPwmStop(PWM_G);
    if (b) IoTPwmStart(PWM_B, (unsigned short)b, 1000); else IoTPwmStop(PWM_B);
    g_led_on = (r || g || b);
}

static void beep(int ms)
{
    if (!g_pwm_ok) return;
    if (ms <= 0) ms = 100;
    if (ms > 2000) ms = 2000;
    IoTPwmStart(PWM_BEEP, 50, 2700);
    usleep(ms * 1000);
    IoTPwmStop(PWM_BEEP);
}

static void motor(int dir, int ms)
{
    if (!g_pwm_ok) return;
    if (ms <= 0) ms = 500;
    if (ms > 3000) ms = 3000;
    IoTPwmStart(PWM_MOTOR, (dir > 0) ? 60 : 40, 1000);
    usleep(ms * 1000);
    IoTPwmStop(PWM_MOTOR);
}

/* ---------------- 传感器 ---------------- */
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
    unsigned char cmd = 0x10;      /* 连续高分辨率 */
    unsigned char buf[2];
    IoTI2cWrite(I2C_ENV, ADDR_BH1750, &cmd, 1);
    usleep(180 * 1000);
    if (IoTI2cRead(I2C_ENV, ADDR_BH1750, buf, 2) != IOT_SUCCESS) return 0;
    int raw = (buf[0] << 8) | buf[1];
    g_lux = (int)(raw / 1.2f);
    return 1;
}

static int gas_read(void)
{
    unsigned short v = 0;
    if (IoTAdcGetVal(ADC_GAS, &v) != IOT_SUCCESS) return 0;
    g_gas = v;
    return 1;
}

static int pir_read(void)
{
    IotGpioValue v = IOT_GPIO_VALUE0;
    IoTGpioGetInputVal(PIN_PIR, &v);
    return (v == IOT_GPIO_VALUE1) ? 1 : 0;
}

/* ---------------- LCD 仪表盘 ---------------- */
static void lcd_dashboard(void)
{
    char buf[40];
    if (!g_lcd_ok) return;

    lcd_fill(0, 0, LCD_W, LCD_H, LCD_WHITE);

    /* 标题 */
    lcd_show_chinese(8, 6, "芯宿智控", LCD_BLUE, LCD_WHITE, 24, 0);
    lcd_show_string(120, 16, "ROOM ENV", LCD_GRAY, LCD_WHITE, 16, 0);
    lcd_draw_line(0, 36, LCD_W, 36, LCD_BLUE);

    /* 温度 */
    lcd_show_chinese(8, 48, "温度", LCD_BLACK, LCD_WHITE, 24, 0);
    lcd_show_float_num1(80, 48, g_temp, 4, LCD_RED, LCD_WHITE, 24);
    lcd_show_string(190, 56, "C", LCD_RED, LCD_WHITE, 24, 0);

    /* 湿度 */
    lcd_show_chinese(8, 88, "湿度", LCD_BLACK, LCD_WHITE, 24, 0);
    lcd_show_float_num1(80, 88, g_hum, 4, LCD_BLUE, LCD_WHITE, 24);
    lcd_show_string(190, 96, "%", LCD_BLUE, LCD_WHITE, 24, 0);

    /* 光照 */
    lcd_show_chinese(8, 128, "光照", LCD_BLACK, LCD_WHITE, 24, 0);
    lcd_show_int_num(80, 128, (uint16_t)g_lux, 5, LCD_YELLOW, LCD_WHITE, 24);
    lcd_show_string(230, 136, "lx", LCD_YELLOW, LCD_WHITE, 16, 0);

    /* 分隔线 */
    lcd_draw_line(0, 166, LCD_W, 166, LCD_GRAY);

    /* 人体 / 燃气 / 灯 */
    lcd_show_chinese(8, 176, "人体", LCD_BLACK, LCD_WHITE, 16, 0);
    if (g_pir) {
        lcd_show_chinese(60, 176, "有人", LCD_RED, LCD_WHITE, 16, 0);
    } else {
        lcd_show_chinese(60, 176, "无人", LCD_GRAY, LCD_WHITE, 16, 0);
    }

    lcd_show_chinese(150, 176, "燃气", LCD_BLACK, LCD_WHITE, 16, 0);
    if (g_gas > 2500) {
        lcd_show_chinese(198, 176, "报警", LCD_RED, LCD_WHITE, 16, 0);
    } else {
        lcd_show_chinese(198, 176, "正常", LCD_GREEN, LCD_WHITE, 16, 0);
    }

    lcd_show_chinese(8, 204, "灯光", LCD_BLACK, LCD_WHITE, 16, 0);
    if (g_led_on) {
        lcd_show_chinese(60, 204, "已开", LCD_YELLOW, LCD_WHITE, 16, 0);
    } else {
        lcd_show_chinese(60, 204, "已关", LCD_GRAY, LCD_WHITE, 16, 0);
    }

    /* 底部状态 */
    snprintf(buf, sizeof(buf), "gas raw: %d", g_gas);
    lcd_show_string(8, 226, (const uint8_t *)buf, LCD_GRAY, LCD_WHITE, 12, 0);
}
/* ---------------- shell ---------------- */
static int zh_shell_cmd(int argc, const char **argv)
{
    if (argc < 2) { zh_print("ZH|ACK|HELP|OK|%s\r\n", ZH_VER); return 0; }
    const char *sub = argv[1];

    if (strcmp(sub, "ping") == 0) {
        zh_print("ZH|ACK|PING|OK|%s|pir=%d|gas=%d|pwm=%d\r\n",
                 ZH_VER, g_pir, g_gas, g_pwm_ok);
    } else if (strcmp(sub, "env") == 0) {
        int ok1 = sht30_read();
        int ok2 = bh1750_read();
        zh_print("ZH|ACK|ENV|%s|t=%.1f|h=%.1f|lux=%d\r\n",
                 (ok1 && ok2) ? "OK" : "PART",
                 g_temp, g_hum, g_lux);
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
        int ms = (argc > 2) ? atoi(argv[2]) : 120;
        beep(ms);
        zh_print("ZH|ACK|BEEP|OK|%d\r\n", ms);
    } else if (strcmp(sub, "motor") == 0) {
        int dir = (argc > 2) ? atoi(argv[2]) : 1;
        int ms = (argc > 3) ? atoi(argv[3]) : 500;
        motor(dir, ms);
        zh_print("ZH|ACK|MOTOR|OK|%d|%d\r\n", dir, ms);
    } else if (strcmp(sub, "pir") == 0) {
        zh_print("ZH|ACK|PIR|%d\r\n", pir_read());
    } else if (strcmp(sub, "gas") == 0) {
        gas_read();
        zh_print("ZH|ACK|GAS|%d\r\n", g_gas);
    } else if (strcmp(sub, "lcd") == 0) {
        unsigned int r = lcd_init();
        g_lcd_ok = (r == 0) ? 1 : 0;
        zh_print("ZH|ACK|LCD|init=%u|ok=%d\r\n", r, g_lcd_ok);
        if (g_lcd_ok) {
            lcd_fill(0, 0, LCD_W, LCD_H, LCD_RED);
            lcd_show_string(20, 100, "LCD TEST OK", LCD_WHITE, LCD_RED, 24, 0);
            zh_print("ZH|ACK|LCD|drawn\r\n");
        }    } else if (strcmp(sub, "auto") == 0) {
        if (argc > 2) g_auto_light = atoi(argv[2]) ? 1 : 0;
        zh_print("ZH|ACK|AUTO|%d\r\n", g_auto_light);
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
    int last_pir = 0;
    int gas_alarm = 0;

    osDelay(5000);
    zh_print("[zh] lcd init...\r\n");
    if (lcd_init() == 0) {
        g_lcd_ok = 1;
        lcd_fill(0, 0, LCD_W, LCD_H, LCD_WHITE);
        lcd_show_chinese(40, 100, "启动中", LCD_BLUE, LCD_WHITE, 32, 0);
        zh_print("[zh] lcd ok\r\n");
    } else {
        zh_print("[zh] lcd failed\r\n");
    }
    zh_print("[zh] %s ready lcd=%d pwm=%d\r\n", ZH_VER, g_lcd_ok, g_pwm_ok);

    while (1) {
        unsigned int t = (unsigned int)(osKernelGetTickCount() * 1000u /
                                        (osKernelGetTickFreq() ? osKernelGetTickFreq() : 1));

        /* 人体感应：上升沿自动开灯 */
        int p = pir_read();
        if (p != last_pir) {
            last_pir = p;
            g_pir = p;
            zh_print("ZH|EVT|PIR|%d\r\n", p);
            if (p && g_auto_light) {
                rgb_set(100, 80, 40);          /* 暖白光 */
            }
        }

        /* 燃气：每 2 秒采一次 */
        if (n % 40 == 0) {
            if (gas_read()) {
                if (g_gas > 2500 && !gas_alarm) {
                    gas_alarm = 1;
                    zh_print("ZH|EVT|GAS|ALARM|%d\r\n", g_gas);
                    beep(600);
                } else if (g_gas <= 2200 && gas_alarm) {
                    gas_alarm = 0;
                    zh_print("ZH|EVT|GAS|CLEAR|%d\r\n", g_gas);
                }
            }
        }

        if (n % 20 == 0) {
            lcd_dashboard();
        }

        n++;
        if (n % 150 == 0) {
            zh_print("[zh] alive #%u pir=%d gas=%d led=%d\r\n", n, g_pir, g_gas, g_led_on);
        }
        osDelay(50);
    }
    return NULL;
}

static void zh_entry(void)
{
    g_print_mutex = osMutexNew(NULL);
    zh_print("\r\n[zh] entry start\r\n");

    /* 先把命令注册上，保证后面的初始化即使卡住也能诊断 */
    unsigned int r = osCmdReg(ZH_CMD_TYPE_STD, "zh", ZH_XARGS, (zh_cmd_cb_t)zh_shell_cmd);
    zh_print("[zh] cmd registered reg=%u\r\n", r);

    zh_print("[zh] i2c init...\r\n");
    IoTI2cInit(I2C_ENV, EI2C_FRE_100K);
    zh_print("[zh] i2c done\r\n");

    zh_print("[zh] gpio/pir...\r\n");
    IoTGpioInit(PIN_PIR);
    IoTGpioSetDir(PIN_PIR, IOT_GPIO_DIR_IN);
    IoTGpioInit(PIN_LED);
    IoTGpioSetDir(PIN_LED, IOT_GPIO_DIR_OUT);
    IoTGpioSetOutputVal(PIN_LED, IOT_GPIO_VALUE0);
    zh_print("[zh] gpio done\r\n");

    zh_print("[zh] adc...\r\n");
    IoTAdcInit(ADC_GAS);
    IoTAdcInit(ADC_KEY);
    zh_print("[zh] adc done\r\n");

    zh_print("[zh] pwm...\r\n");
    if (IoTPwmInit(PWM_R) == IOT_SUCCESS &&
        IoTPwmInit(PWM_G) == IOT_SUCCESS &&
        IoTPwmInit(PWM_B) == IOT_SUCCESS &&
        IoTPwmInit(PWM_BEEP) == IOT_SUCCESS &&
        IoTPwmInit(PWM_MOTOR) == IOT_SUCCESS) {
        g_pwm_ok = 1;
    }
    zh_print("[zh] pwm done ok=%d\r\n", g_pwm_ok);

    /* LCD 留到线程里、开机 5 秒后再初始化，避免拖住启动 */
    zh_print("[zh] thread start\r\n");

    osThreadAttr_t a = {0};
    a.stack_size = 8192;
    a.priority = osPriorityNormal;
    a.name = "zh_main";
    osThreadNew((osThreadFunc_t)zh_task, NULL, &a);
}

SYS_RUN(zh_entry);
