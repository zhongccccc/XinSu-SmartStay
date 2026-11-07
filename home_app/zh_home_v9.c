/*
 * 芯宿·智控 —— 智能家居板 v9（主指标式仪表盘）
 *
 * 版式参考 M5Stack 320x240 布局规范：
 *   顶部 34px 标题栏 + 中部主指标（温度，占一半视觉面积）+ 底部分栏次要指标
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
#define ADC_KEY          7

/* 按键电压（厂商手册）：不按 3.3V / K3 0.01V / K4 1.0V / K5 1.65V / K6 0.55V
 * ADC 10bit，raw = V * 1024 / 3.3 */
#define KEY_NONE_RAW     1000
#define KEY_K3_RAW       3
#define KEY_K4_RAW       310
#define KEY_K5_RAW       512
#define KEY_K6_RAW       171
#define KEY_TOL          60
#define ZH_VER           "rk2206-home-v26"

#define C_BG     0x0000
#define C_HEAD   0x0920
#define C_LINE   0x2104
#define C_WHITE  0xFFFF
#define C_SUB    0x8C71
#define C_CYAN   0x07FF
#define C_GREEN  0x07E0
#define C_RED    0xF800
#define C_YELLOW 0xFFE0
#define C_ORANGE 0xFD20

static osMutexId_t g_print_mutex;
static int inited_i2c = 0, inited_adc = 0, inited_pwm = 0, inited_lcd = 0, inited_gpio = 0;
static float g_temp = -100.0f, g_hum = -100.0f;
static int g_lux = -1, g_gas = 0, g_pir = 0, g_led_on = 0, g_auto = 1;
static unsigned int g_light_until = 0;   /* 到这个时刻自动关灯 */
#define LIGHT_KEEP_MS  5000              /* 测试用：无人后 5 秒关灯 */

static unsigned int zh_now_ms(void)
{
    uint32_t tick = osKernelGetTickCount();
    uint32_t freq = osKernelGetTickFreq();
    return freq ? (unsigned int)((uint64_t)tick * 1000u / freq) : tick;
}

/* 上次绘制值，用于"只在变化时刷新" */
/* 旧 dirty 变量已由下方新版替代 */

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
static int g_fan_duty = 0;

static void ensure_pwm(void)
{
    if (inited_pwm) return;
    inited_pwm = 1;
    IoTPwmInit(PWM_R); IoTPwmInit(PWM_G); IoTPwmInit(PWM_B);
    IoTPwmInit(PWM_BEEP); IoTPwmInit(PWM_MOTOR);
    /* 上电先全部停掉，避免开机红灯 */
    IoTPwmStop(PWM_R); IoTPwmStop(PWM_G); IoTPwmStop(PWM_B);
    IoTPwmStop(PWM_MOTOR); IoTPwmStop(PWM_BEEP);
}

static int sht30_read(void)
{
    unsigned char cmd[2] = {0x2C, 0x06};
    unsigned char buf[6];
    if (IoTI2cWrite(I2C_ENV, ADDR_SHT30, cmd, 2) != IOT_SUCCESS) return 0;
    usleep(20 * 1000);
    if (IoTI2cRead(I2C_ENV, ADDR_SHT30, buf, 6) != IOT_SUCCESS) return 0;
    g_temp = -45.0f + 175.0f * (float)((buf[0] << 8) | buf[1]) / 65535.0f;
    g_hum = 100.0f * (float)((buf[3] << 8) | buf[4]) / 65535.0f;
    return 1;
}
static int bh1750_read(void)
{
    unsigned char cmd = 0x10, buf[2];
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

/* 读按键：返回 '3' '4' '5' '6' 或 0 */
static char key_read(void)
{
    unsigned short v = 0;
    if (IoTAdcGetVal(ADC_KEY, &v) != IOT_SUCCESS) return 0;
    int raw = (int)v;
    if (raw > KEY_NONE_RAW) return 0;
    if (raw < KEY_K3_RAW + KEY_TOL) return '3';
    if (raw > KEY_K6_RAW - KEY_TOL && raw < KEY_K6_RAW + KEY_TOL) return '6';
    if (raw > KEY_K4_RAW - KEY_TOL && raw < KEY_K4_RAW + KEY_TOL) return '4';
    if (raw > KEY_K5_RAW - KEY_TOL && raw < KEY_K5_RAW + KEY_TOL) return '5';
    return 0;
}

/* 风扇：duty 1~99，0 = 停 */
static void fan_set(int duty)
{
    ensure_pwm();
    if (duty < 0) duty = 0;
    if (duty > 99) duty = 99;
    if (duty == 0) IoTPwmStop(PWM_MOTOR);
    else IoTPwmStart(PWM_MOTOR, (unsigned short)duty, 1000);
    g_fan_duty = duty;
}

/* ---------------- 版式（黑白 · 中文 · 局部刷新） ----------------
 * 320x240
 *   y=6   温度 | 湿度         y=72  光照 | 燃气
 *   y=138 人体（满宽）          y=178 风扇 | 灯
 * 只重画数值变化的卡片，避免整屏重绘闪烁
 */
#define C_BLACK  0x0000
#define C_WHITE  0xFFFF
#define C_GRAY   0x8410

/* 上次显示的值，用于判断是否需要重画 */
static int d_temp10 = -9999, d_hum = -9999, d_lux = -9999, d_gas = -9999;
static int d_pir = -1, d_fan = -1, d_led = -1;

static void box(int x, int y, int w, int h, uint16_t color)
{
    lcd_fill(x, y, x + w - 1, y + h - 1, color);
}

/* 画一张卡片（含边框、标签、数值、单位） */
static void card(int x, int y, int w, const char *label, const char *value,
                 const char *unit)
{
    box(x, y, w, 60, C_WHITE);
    box(x + 2, y + 2, w - 4, 56, C_BLACK);
    lcd_show_chinese(x + 8, y + 6, (uint8_t *)label, C_GRAY, C_BLACK, 16, 0);
    lcd_show_string(x + 8, y + 28, (const uint8_t *)value, C_WHITE, C_BLACK, 24, 0);
    if (unit && unit[0]) {
        lcd_show_string(x + w - 30, y + 34, (const uint8_t *)unit, C_GRAY, C_BLACK, 16, 0);
    }
}

/* 人体状态条 */
static void pir_banner(int active)
{
    if (active) {
        box(8, 138, 304, 34, C_WHITE);
        lcd_show_chinese(18, 147, "人体", C_BLACK, C_WHITE, 16, 0);
        lcd_show_chinese(210, 147, "有人", C_BLACK, C_WHITE, 16, 0);
    } else {
        box(8, 138, 304, 34, C_WHITE);
        box(10, 140, 300, 30, C_BLACK);
        lcd_show_chinese(18, 147, "人体", C_WHITE, C_BLACK, 16, 0);
        lcd_show_chinese(210, 147, "无人", C_GRAY, C_BLACK, 16, 0);
    }
}

/* 半宽开关：开=白底黑字，关=黑底白字 */
static void sw(int x, int y, const char *label, int on)
{
    if (on) {
        box(x, y, 148, 40, C_WHITE);
        lcd_show_chinese(x + 12, y + 12, (uint8_t *)label, C_BLACK, C_WHITE, 16, 0);
        lcd_show_chinese(x + 104, y + 12, "开", C_BLACK, C_WHITE, 16, 0);
    } else {
        box(x, y, 148, 40, C_WHITE);
        box(x + 2, y + 2, 144, 36, C_BLACK);
        lcd_show_chinese(x + 12, y + 12, (uint8_t *)label, C_WHITE, C_BLACK, 16, 0);
        lcd_show_chinese(x + 104, y + 12, "关", C_GRAY, C_BLACK, 16, 0);
    }
}

static void draw_temp(void)
{
    char b[16];
    snprintf(b, sizeof(b), "%.1f", g_temp < -90 ? 0.0f : g_temp);
    card(8, 6, 148, "温度", b, "C");
}
static void draw_hum(void)
{
    char b[16];
    snprintf(b, sizeof(b), "%.0f", g_hum < 0 ? 0.0f : g_hum);
    card(164, 6, 148, "湿度", b, "%");
}
static void draw_lux(void)
{
    char b[16];
    snprintf(b, sizeof(b), "%d", g_lux < 0 ? 0 : g_lux);
    card(8, 72, 148, "光照", b, "lx");
}
static void draw_gas(void)
{
    char b[16];
    snprintf(b, sizeof(b), "%d", g_gas);
    card(164, 72, 148, "燃气", b, "");
}

/* 全量重画（开机 / 手动刷新） */
static void dash_full(void)
{
    char b[16];

    box(0, 0, LCD_W, LCD_H, C_BLACK);

    snprintf(b, sizeof(b), "%.1f", g_temp < -90 ? 0.0f : g_temp);
    card(8, 6, 148, "温度", b, "C");
    snprintf(b, sizeof(b), "%.0f", g_hum < 0 ? 0.0f : g_hum);
    card(164, 6, 148, "湿度", b, "%");
    snprintf(b, sizeof(b), "%d", g_lux < 0 ? 0 : g_lux);
    card(8, 72, 148, "光照", b, "lx");
    snprintf(b, sizeof(b), "%d", g_gas);
    card(164, 72, 148, "燃气", b, "");

    pir_banner(g_pir);
    sw(8, 178, "风扇", g_fan_duty > 0);
    sw(164, 178, "灯", g_led_on > 0);

    d_temp10 = (int)(g_temp * 10);
    d_hum = (int)g_hum;
    d_lux = g_lux;
    d_gas = g_gas;
    d_pir = g_pir ? 1 : 0;
    d_fan = g_fan_duty > 0 ? 1 : 0;
    d_led = g_led_on > 0 ? 1 : 0;
}

/* 增量刷新：只重画变化的那一块 */
static void dash_sync(void)
{
    int t10 = (int)(g_temp * 10);
    int h = (int)g_hum;
    int f = g_fan_duty > 0 ? 1 : 0;
    int l = g_led_on > 0 ? 1 : 0;
    int p = g_pir ? 1 : 0;

    if (t10 != d_temp10) { d_temp10 = t10; draw_temp(); }
    if (h != d_hum)      { d_hum = h;       draw_hum(); }
    if (g_lux != d_lux)  { d_lux = g_lux;   draw_lux(); }
    /* 燃气抖动较大，变化超过 8 才重画 */
    if (abs(g_gas - d_gas) > 8) { d_gas = g_gas; draw_gas(); }
    if (p != d_pir)      { d_pir = p;       pir_banner(p); }
    if (f != d_fan)      { d_fan = f;       sw(8, 178, "风扇", f); }
    if (l != d_led)      { d_led = l;       sw(164, 178, "灯", l); }
}

/* ---------------- shell ---------------- */
static int zh_shell_cmd(int argc, const char **argv)
{
    if (argc < 2) { zh_print("ZH|ACK|HELP|OK|%s\r\n", ZH_VER); return 0; }
    const char *sub = argv[1];

    if (strcmp(sub, "ping") == 0) {
        zh_print("ZH|ACK|PING|OK|%s|i2c=%d|adc=%d|pwm=%d|lcd=%d|pir=%d\r\n",
                 ZH_VER, inited_i2c, inited_adc, inited_pwm, inited_lcd, g_pir);
    } else if (strcmp(sub, "env") == 0) {
        ensure_i2c();
        int a = sht30_read(), b = bh1750_read();
        zh_print("ZH|ACK|ENV|%s|t=%.1f|h=%.1f|lux=%d\r\n",
                 (a && b) ? "OK" : "PART", g_temp, g_hum, g_lux);
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
    } else if (strcmp(sub, "rgb") == 0) {
        int r = (argc > 2) ? atoi(argv[2]) : 0;
        int g = (argc > 3) ? atoi(argv[3]) : 0;
        int b = (argc > 4) ? atoi(argv[4]) : 0;
        rgb_set(r, g, b);
        if (inited_lcd) { dash_sync(); }
        zh_print("ZH|ACK|RGB|OK\r\n");
    } else if (strcmp(sub, "rgboff") == 0) {
        rgb_set(0, 0, 0);
        if (inited_lcd) { dash_sync(); }
        zh_print("ZH|ACK|RGB|OFF\r\n");
    } else if (strcmp(sub, "beep") == 0) {
        ensure_pwm();
        int ms = (argc > 2) ? atoi(argv[2]) : 100;
        IoTPwmStart(PWM_BEEP, 50, 2700);
        usleep(ms * 1000);
        IoTPwmStop(PWM_BEEP);
        zh_print("ZH|ACK|BEEP|OK\r\n");
    } else if (strcmp(sub, "redraw") == 0) {
        if (inited_lcd) dash_full();
        zh_print("ZH|ACK|REDRAW|%d\r\n", inited_lcd);} else if (strcmp(sub, "inv") == 0) {
        int on = (argc > 2) ? atoi(argv[2]) : 1;
        lcd_invert((unsigned char)(on ? 1 : 0));
        if (inited_lcd) dash_full();
        zh_print("ZH|ACK|INV|%d\r\n", on);} else if (strcmp(sub, "light") == 0) {
        if (argc > 2 && strcmp(argv[2], "on") == 0) {
            /* 宿主机命令：保持亮着，直到收到 off（迎宾模式用） */
            rgb_set(99, 99, 99);
            g_light_until = 0;
        } else if (argc > 2 && strcmp(argv[2], "auto") == 0) {
            /* 交回给自动逻辑（有人亮、无人 N 秒灭） */
            g_light_until = zh_now_ms() + LIGHT_KEEP_MS;
        } else {
            rgb_set(0, 0, 0);
            g_light_until = 0;
        }
        if (inited_lcd) { dash_sync(); }
        zh_print("ZH|ACK|LIGHT|%d\r\n", g_led_on);
    } else if (strcmp(sub, "fan") == 0) {
        int d = 0;
        if (argc > 2) {
            if (strcmp(argv[2], "on") == 0) d = 60;
            else if (strcmp(argv[2], "off") == 0) d = 0;
            else d = atoi(argv[2]);
        }
        fan_set(d);
        zh_print("ZH|ACK|FAN|%d\r\n", g_fan_duty);
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
    char last_key = 0;

    osDelay(800);
    unsigned int reg = osCmdReg(ZH_CMD_TYPE_STD, "zh", ZH_XARGS, (zh_cmd_cb_t)zh_shell_cmd);
    zh_print("[zh] %s ready reg=%u\r\n", ZH_VER, reg);

    ensure_gpio();
    ensure_i2c();
    ensure_adc();
    ensure_pwm();
    rgb_set(0, 0, 0);
    fan_set(0);
    IoTAdcInit(ADC_KEY);
    sht30_read();
    bh1750_read();

    if (lcd_init() == 0) {
        inited_lcd = 1;
        dash_full();
        zh_print("[zh] lcd ok\r\n");
    } else {
        zh_print("[zh] lcd failed\r\n");
    }

    while (1) {
        IotGpioValue v = IOT_GPIO_VALUE0;
        IoTGpioGetInputVal(PIN_PIR, &v);
        int p = (v == IOT_GPIO_VALUE1);
        if (p != last_pir) {
            last_pir = p;
            g_pir = p;
            zh_print("ZH|EVT|PIR|%d\r\n", p);
            /* 人体感应只上报状态，不再自动开关灯 */
            if (inited_lcd) { dash_sync(); }
        }

        /* 板载按键 */
        {
            char k = key_read();
            if (k != last_key) {
                last_key = k;
                if (k) {
                    zh_print("ZH|EVT|KEY|%c\r\n", k);
                    ensure_pwm();
                    if (k == '6') {                    /* K6：开关灯 */
                        if (g_led_on) { rgb_set(0, 0, 0); g_light_until = 0; }
                        else { rgb_set(99, 99, 99); g_light_until = zh_now_ms() + LIGHT_KEEP_MS; }
                        if (inited_lcd) { dash_sync(); }
                    } else if (k == '4') {             /* K4：开关风扇 */
                        fan_set(g_fan_duty ? 0 : 60);
                        if (inited_lcd) { dash_sync(); }
                    } else if (k == '5') {             /* K5：风扇调速 */
                        if (g_fan_duty == 0) fan_set(30);
                        else if (g_fan_duty < 60) fan_set(60);
                        else if (g_fan_duty < 99) fan_set(99);
                        else fan_set(0);
                        if (inited_lcd) { dash_sync(); }
                    } else if (k == '3') {             /* K3：一键全关 */
                        rgb_set(0, 0, 0);
                        g_light_until = 0;
                        fan_set(0);
                        if (inited_lcd) { dash_sync(); }
                    }
                }
            }
        }

        /* 无人一段时间后自动关灯 */
        if (g_led_on && g_light_until && (int)(g_light_until - zh_now_ms()) <= 0) {
            rgb_set(0, 0, 0);
            g_light_until = 0;
            zh_print("ZH|EVT|LIGHT|off\r\n");
            if (inited_lcd) { dash_sync(); }
        }

        if (n % 8 == 0) {
            sht30_read();
            bh1750_read();
            unsigned short gv = 0;
            IoTAdcGetVal(ADC_GAS, &gv);
            g_gas = gv;
            if (inited_lcd) { dash_sync(); }
        }

        n++;
        if (n % 20 == 0) {
            zh_print("[zh] alive #%u t=%.1f h=%.1f lux=%d gas=%d pir=%d\r\n",
                     n, g_temp, g_hum, g_lux, g_gas, g_pir);
        }
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
