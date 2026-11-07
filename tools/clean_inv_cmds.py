# -*- coding: utf-8 -*-
"""删掉用不到的 inv/invsw/madctl 命令（v24 黑白版不再需要）。"""
import re
P = r"E:\zhikong\home_app\zh_home_v9.c"
s = open(P, encoding="utf-8").read()

# 删三个命令分支
for name in ("invsw", "inv", "madctl"):
    pat = re.compile(r'\n\s*\} else if \(strcmp\(sub, "%s"\) == 0\) \{.*?\n\s*(?=\} else if|\} else \{)' % name, re.S)
    s2 = pat.sub("", s, count=1)
    if s2 != s:
        print("已删除命令:", name)
        s = s2

# 兜底：如果还有 g_inv 引用，定义它
if "g_inv" in s and "static int g_inv" not in s:
    s = s.replace("static osMutexId_t g_print_mutex;",
                  "static int g_inv = 0;\nstatic osMutexId_t g_print_mutex;", 1)
    print("补了 g_inv 定义")

open(P, "w", encoding="utf-8").write(s)
print("剩余 inv 引用:", s.count("g_inv"))
