# -*- coding: utf-8 -*-
"""把 zh 命令注册提前到初始化之前，并逐步打印初始化进度。"""
P = r"E:\zhikong\home_app\zh_home.c"
s = open(P, encoding="utf-8").read()

start = s.index("static void zh_entry(void)")
end = s.index("SYS_RUN(zh_entry);")

NEW = '''static void zh_entry(void)
{
    g_print_mutex = osMutexNew(NULL);
    zh_print("\\r\\n[zh] entry start\\r\\n");

    /* 先把命令注册上，保证后面的初始化即使卡住也能诊断 */
    unsigned int r = osCmdReg(ZH_CMD_TYPE_STD, "zh", ZH_XARGS, (zh_cmd_cb_t)zh_shell_cmd);
    zh_print("[zh] cmd registered reg=%u\\r\\n", r);

    zh_print("[zh] i2c init...\\r\\n");
    IoTI2cInit(I2C_ENV, EI2C_FRE_100K);
    zh_print("[zh] i2c done\\r\\n");

    zh_print("[zh] gpio/pir...\\r\\n");
    IoTGpioInit(PIN_PIR);
    IoTGpioSetDir(PIN_PIR, IOT_GPIO_DIR_IN);
    IoTGpioInit(PIN_LED);
    IoTGpioSetDir(PIN_LED, IOT_GPIO_DIR_OUT);
    IoTGpioSetOutputVal(PIN_LED, IOT_GPIO_VALUE0);
    zh_print("[zh] gpio done\\r\\n");

    zh_print("[zh] adc...\\r\\n");
    IoTAdcInit(ADC_GAS);
    IoTAdcInit(ADC_KEY);
    zh_print("[zh] adc done\\r\\n");

    zh_print("[zh] pwm...\\r\\n");
    if (IoTPwmInit(PWM_R) == IOT_SUCCESS &&
        IoTPwmInit(PWM_G) == IOT_SUCCESS &&
        IoTPwmInit(PWM_B) == IOT_SUCCESS &&
        IoTPwmInit(PWM_BEEP) == IOT_SUCCESS &&
        IoTPwmInit(PWM_MOTOR) == IOT_SUCCESS) {
        g_pwm_ok = 1;
    }
    zh_print("[zh] pwm done ok=%d\\r\\n", g_pwm_ok);

    /* LCD 留到线程里、开机 5 秒后再初始化，避免拖住启动 */
    zh_print("[zh] thread start\\r\\n");

    osThreadAttr_t a = {0};
    a.stack_size = 8192;
    a.priority = osPriorityNormal;
    a.name = "zh_main";
    osThreadNew((osThreadFunc_t)zh_task, NULL, &a);
}

'''
s = s[:start] + NEW + s[end:]

# 线程里：开机 5 秒后再初始化 LCD，并保留任务循环
s = s.replace('''    osDelay(300);
    unsigned int r = osCmdReg(ZH_CMD_TYPE_STD, "zh", ZH_XARGS, (zh_cmd_cb_t)zh_shell_cmd);
    zh_print("[zh] %s ready reg=%u\\r\\n", ZH_VER, r);''',
'''    osDelay(5000);
    zh_print("[zh] lcd init...\\r\\n");
    if (lcd_init() == 0) {
        g_lcd_ok = 1;
        lcd_fill(0, 0, LCD_W, LCD_H, LCD_WHITE);
        lcd_show_chinese(40, 100, "启动中", LCD_BLUE, LCD_WHITE, 32, 0);
        zh_print("[zh] lcd ok\\r\\n");
    } else {
        zh_print("[zh] lcd failed\\r\\n");
    }
    zh_print("[zh] %s ready lcd=%d pwm=%d\\r\\n", ZH_VER, g_lcd_ok, g_pwm_ok);''', 1)

s = s.replace('ZH_VER           "rk2206-home-v2"', 'ZH_VER           "rk2206-home-v3"')
open(P, "w", encoding="utf-8").write(s)
print("patched home v3")
