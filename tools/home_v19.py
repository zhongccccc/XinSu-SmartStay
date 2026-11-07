# -*- coding: utf-8 -*-
"""v19：删除人体感应自动开关灯（PIR 只上报状态，不再控制灯）。"""
P = r"E:\zhikong\home_app\zh_home_v9.c"
s = open(P, encoding="utf-8").read()

s = s.replace('ZH_VER           "rk2206-home-v18"', 'ZH_VER           "rk2206-home-v19"')

OLD = """            if (p && g_auto) {
                rgb_set(99, 99, 99);
                g_light_until = 0;
            }"""
NEW = """            /* 人体感应只上报状态，不再自动开关灯（按要求移除） */"""
if OLD in s:
    s = s.replace(OLD, NEW, 1)
    print("已移除 PIR 自动开灯")
else:
    import re
    m = re.search(r"\n\s*if \(p && g_auto\) \{[^}]*\}\n", s)
    if m:
        s = s[:m.start()] + "\n            /* 人体感应只上报状态，不再自动开关灯 */\n" + s[m.end():]
        print("已用正则移除")
    else:
        print("!! 未找到 PIR 开灯代码")

# 关闭 auto 默认值，避免按键或别处再触发
s = s.replace("static int g_auto = 1;", "static int g_auto = 0;")

open(P, "w", encoding="utf-8").write(s)
print("版本:", [l.strip() for l in s.splitlines() if "ZH_VER" in l and "define" in l])
