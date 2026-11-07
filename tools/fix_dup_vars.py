# -*- coding: utf-8 -*-
"""删掉 v10 遗留的旧 dirty 变量（与新版重复）。"""
P = r"E:\zhikong\home_app\zh_home_v9.c"
s = open(P, encoding="utf-8").read()

OLD = """static int d_lux = -99999, d_gas_alarm = -1, d_led = -1, d_pir = -1;
static float d_temp = -999.0f, d_hum = -999.0f;"""
if OLD in s:
    s = s.replace(OLD, "/* 旧 dirty 变量已由下方新版替代 */", 1)
    open(P, "w", encoding="utf-8").write(s)
    print("已删除旧变量")
else:
    print("未匹配，逐行检查")
    for i, line in enumerate(s.splitlines(), 1):
        if "d_gas_alarm" in line or ("d_temp" in line and "float" in line):
            print("  可能残留 L%d: %s" % (i, line.strip()))
