#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成最小版 zh_home.c：只注册命令 + 心跳，不初始化任何外设。"""
import re

P = r"E:\zhikong\home_app\zh_home.c"
s = open(P, encoding="utf-8").read()

start = s.index("static void zh_entry(void)")
end = s.index("SYS_RUN(zh_entry);")

NEW = '''static void zh_entry(void)
{
    g_print_mutex = osMutexNew(NULL);
    zh_print("\\r\\n[zh] MINIMAL entry\\r\\n");

    g_lcd_ok = 0;
    g_pwm_ok = 0;

    osThreadAttr_t a = {0};
    a.stack_size = 8192;
    a.priority = osPriorityNormal;
    a.name = "zh_main";
    osThreadNew((osThreadFunc_t)zh_task, NULL, &a);
}

'''
s = s[:start] + NEW + s[end:]

# 任务里：去掉 LCD 初始化 和 传感器读取，只留心跳
start2 = s.index("static void *zh_task(void *arg)")
end2 = s.index("static void zh_entry(void)")
NEWTASK = '''static void *zh_task(void *arg)
{
    (void)arg;
    unsigned int n = 0;

    osDelay(300);
    unsigned int r = osCmdReg(ZH_CMD_TYPE_STD, "zh", ZH_XARGS, (zh_cmd_cb_t)zh_shell_cmd);
    zh_print("[zh] %s ready reg=%u\\r\\n", ZH_VER, r);

    while (1) {
        n++;
        if (n % 20 == 0) {
            zh_print("[zh] alive #%u\\r\\n", n);
        }
        osDelay(200);
    }
    return NULL;
}

'''
s = s[:start2] + NEWTASK + s[end2:]

s = s.replace('ZH_VER           "rk2206-home-v3"', 'ZH_VER           "rk2206-home-min"')
open(P, "w", encoding="utf-8").write(s)
print("已生成最小版")
