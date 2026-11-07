# -*- coding: utf-8 -*-
"""v18：宿主机下发的开灯命令改为"保持"，不再被 5 秒定时器关掉。

PIR 触发的灯仍然 5 秒后自动关（测试值），按键 K6 也仍是 5 秒。
但 `zh light on`（入驻迎宾模式用）会一直亮，直到 `zh light off`。
额外新增 `zh light auto` 恢复自动熄灭。
"""
P = r"E:\zhikong\home_app\zh_home_v9.c"
s = open(P, encoding="utf-8").read()

s = s.replace('ZH_VER           "rk2206-home-v17"', 'ZH_VER           "rk2206-home-v18"')
s = s.replace('ZH_VER           "rk2206-home-v16"', 'ZH_VER           "rk2206-home-v18"')

OLD = """    } else if (strcmp(sub, "light") == 0) {
        if (argc > 2 && strcmp(argv[2], "on") == 0) {
            rgb_set(99, 99, 99);
            g_light_until = zh_now_ms() + LIGHT_KEEP_MS;
        } else if (argc > 2 && strcmp(argv[2], "auto") == 0) {
            g_light_until = zh_now_ms() + LIGHT_KEEP_MS;
        } else {
            rgb_set(0, 0, 0);
            g_light_until = 0;
        }"""

NEW = """    } else if (strcmp(sub, "light") == 0) {
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
        }"""

if OLD in s:
    s = s.replace(OLD, NEW, 1)
    print("light 命令已改为保持")
else:
    # 兼容旧文本（99 或 100 占空比）
    import re
    m = re.search(r'\} else if \(strcmp\(sub, "light"\) == 0\) \{.*?\n        \}\n', s, re.S)
    if m:
        s = s[:m.start()] + NEW + "\n" + s[m.end():]
        print("light 命令已替换（正则）")
    else:
        print("!! 未匹配 light 命令块")

open(P, "w", encoding="utf-8").write(s)
print("版本:", [l for l in s.splitlines() if "ZH_VER" in l and "define" in l])
