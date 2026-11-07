/*
 * 芯宿·智控 —— 智能门锁板 诊断固件 v5
 *
 * 目的：先用最小代码确认"板子活着 + 串口通 + 命令能收"，再逐项加外设。
 * 相比 v3 只改三件事：
 *   1) 开机立即刹车（IA=PC7/23，IB=GPIO1_PD0/56）
 *   2) 每 2 秒打印一次心跳（证明在跑）
 *   3) shell 命令注册延后 2 秒（避免在 OsShellInit 之前注册导致异常）
 * 不再初始化 ADC / PWM / I2C，排除它们导致挂死的可能。
 */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdarg.h>
#include <unistd.h>

#include "ohos_init.h"
#include "cmsis_os2.h"
#include "iot_gpio.h"

#define ZK_CMD_TYPE_STD   1
#define ZK_XARGS          0xFFFFFFFFu
typedef unsigned int (*zk_cmd_cb_t)(unsigned int argc, const char **argv);
extern unsigned int osCmdReg(int cmdType, const char *cmdKey,
                             unsigned int paraNum, zk_cmd_cb_t cmdProc);

#define PIN_MOTOR_IA      23      /* GPIO0_PC7  L9110S_IA */
#define PIN_MOTOR_IB      56      /* GPIO1_PD0  L9110S_IB */
#define ZK_VER            "rk2206-lock-v5-diag"

static volatile int g_registered = 0;
static volatile int g_cmds = 0;

static void zk_print(const char *fmt, ...)
{
    char buf[200];
    va_list ap;
    va_start(ap, fmt);
    int n = vsnprintf(buf, sizeof(buf), fmt, ap);
    va_end(ap);
    if (n > 0) {
        printf("%s", buf);
        fflush(stdout);
    }
}

static void motor_brake(void)
{
    IoTGpioSetOutputVal(PIN_MOTOR_IA, IOT_GPIO_VALUE0);
    IoTGpioSetOutputVal(PIN_MOTOR_IB, IOT_GPIO_VALUE0);
}

/* 收到命令就回一行，便于 K1 判断链路 */
static int zk_shell_cmd(int argc, const char *argv[])
{
    g_cmds++;
    if (argc < 2) {
        zk_print("\r\nZK|ACK|HELP|OK|%s\r\n", ZK_VER);
        return 0;
    }
    const char *sub = argv[1];
    if (strcmp(sub, "ping") == 0) {
        zk_print("\r\nZK|ACK|PING|OK|%s|cmds=%d\r\n", ZK_VER, g_cmds);
    } else if (strcmp(sub, "stop") == 0) {
        motor_brake();
        zk_print("\r\nZK|ACK|STOP|OK\r\n");
    } else if (strcmp(sub, "open") == 0 || strcmp(sub, "close") == 0) {
        /* 诊断版只回 ACK，不驱动电机，避免意外 */
        zk_print("\r\nZK|ACK|%s|OK|diag-no-motor\r\n", sub);
    } else {
        zk_print("\r\nZK|ACK|%s|ERR|unknown\r\n", sub);
    }
    return 0;
}

static void *zk_task(void *arg)
{
    (void)arg;
    unsigned int n = 0;

    /* 等系统起来再注册，避开 shell 尚未初始化的问题 */
    osDelay(200);
    unsigned int r = osCmdReg(ZK_CMD_TYPE_STD, "zk", ZK_XARGS, (zk_cmd_cb_t)zk_shell_cmd);
    g_registered = 1;
    zk_print("\r\n[zk] osCmdReg ret=%u\r\n", r);

    while (1) {
        n++;
        motor_brake();                     /* 每轮都重申刹车 */
        if (n % 4 == 0) {                  /* 约 2 秒一次 */
            zk_print("[zk] alive #%u reg=%d cmds=%d\r\n", n, g_registered, g_cmds);
        }
        osDelay(500);
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

    printf("\r\n[zk] ===== diag firmware %s =====\r\n", ZK_VER);
    printf("[zk] motor braked (IA=23, IB=56)\r\n");
    fflush(stdout);

    osThreadAttr_t a = {0};
    a.stack_size = 4096;
    a.priority = osPriorityNormal;
    a.name = "zk_diag";
    osThreadNew((osThreadFunc_t)zk_task, NULL, &a);
}

SYS_RUN(zk_entry);
