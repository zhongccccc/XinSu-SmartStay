# -*- coding: utf-8 -*-
"""v16：开机熄灯（消除上电红灯）+ 电机当风扇控制 + 灯控制。"""
P = r"E:\zhikong\home_app\zh_home_v9.c"
s = open(P, encoding="utf-8").read()

s = s.replace('ZH_VER           "rk2206-home-v15"', 'ZH_VER           "rk2206-home-v16"')

# 1) 加电机 PWM
s = s.replace('#define PWM_BEEP         EPWMDEV_PWM5_M0',
              '#define PWM_BEEP         EPWMDEV_PWM5_M0\n#define PWM_MOTOR        EPWMDEV_PWM6_M0', 1)

# 2) ensure_pwm 里初始化电机通道，并立即熄灯
s = s.replace('''static void ensure_pwm(void)
{
    if (inited_pwm) return;
    inited_pwm = 1;
    IoTPwmInit(PWM_R); IoTPwmInit(PWM_G); IoTPwmInit(PWM_B); IoTPwmInit(PWM_BEEP);
}''',
'''static int g_fan_duty = 0;

static void ensure_pwm(void)
{
    if (inited_pwm) return;
    inited_pwm = 1;
    IoTPwmInit(PWM_R); IoTPwmInit(PWM_G); IoTPwmInit(PWM_B);
    IoTPwmInit(PWM_BEEP); IoTPwmInit(PWM_MOTOR);
    /* 上电先全部停掉，避免开机红灯 */
    IoTPwmStop(PWM_R); IoTPwmStop(PWM_G); IoTPwmStop(PWM_B);
    IoTPwmStop(PWM_MOTOR); IoTPwmStop(PWM_BEEP);
}''', 1)

# 3) 风扇控制函数
s = s.replace('/* ---------------- 版式 ---------------- */',
'''/* 风扇：duty 1~99，0 = 停 */
static void fan_set(int duty)
{
    ensure_pwm();
    if (duty < 0) duty = 0;
    if (duty > 99) duty = 99;
    if (duty == 0) IoTPwmStop(PWM_MOTOR);
    else IoTPwmStart(PWM_MOTOR, (unsigned short)duty, 1000);
    g_fan_duty = duty;
}

/* ---------------- 版式 ---------------- */''', 1)

# 4) 命令：fan
s = s.replace('''    } else if (strcmp(sub, "auto") == 0) {''',
'''    } else if (strcmp(sub, "fan") == 0) {
        int d = 0;
        if (argc > 2) {
            if (strcmp(argv[2], "on") == 0) d = 60;
            else if (strcmp(argv[2], "off") == 0) d = 0;
            else d = atoi(argv[2]);
        }
        fan_set(d);
        zh_print("ZH|ACK|FAN|%d\\r\\n", g_fan_duty);
    } else if (strcmp(sub, "auto") == 0) {''', 1)

# 5) 开机就初始化 PWM 并熄灯
s = s.replace('''    ensure_gpio();
    ensure_i2c();
    ensure_adc();
    sht30_read();''',
'''    ensure_gpio();
    ensure_i2c();
    ensure_adc();
    ensure_pwm();
    rgb_set(0, 0, 0);
    fan_set(0);
    sht30_read();''', 1)

open(P, "w", encoding="utf-8").write(s)
print("patched v16")
