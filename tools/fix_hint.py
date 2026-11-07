# -*- coding: utf-8 -*-
import re
C = r"E:\zhikong\app\web\style.css"
cs = open(C, encoding="utf-8").read()
new = (".done-hint{position:fixed;left:0;right:0;bottom:44px;text-align:center;\n"
       "  font-size:13px;color:#8fa4c8;letter-spacing:1px;z-index:5}")
cs2, n = re.subn(r"\.done-hint\{[^}]*\}", new, cs)
open(C, "w", encoding="utf-8").write(cs2)
print("替换:", n)
for i, line in enumerate(cs2.splitlines(), 1):
    if ".done-hint" in line:
        print(" L%d: %s" % (i, line.strip()))
