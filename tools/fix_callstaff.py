# -*- coding: utf-8 -*-
"""呼叫前台按钮下移，避免压住右侧卡片。"""
import re
C = r"E:\zhikong\app\web\style.css"
cs = open(C, encoding="utf-8").read()
cs2, n = re.subn(r"\.call-staff\{[^}]*\}",
                 ".call-staff{position:absolute;right:16px;bottom:40px;z-index:30;\n"
                 "  padding:9px 16px;border-radius:12px;font-size:13px;cursor:pointer;\n"
                 "  background:linear-gradient(135deg,rgba(255,150,90,.9),rgba(255,90,110,.9));\n"
                 "  color:#2a0508;border:0;font-weight:700}",
                 cs)
open(C, "w", encoding="utf-8").write(cs2)
print("替换:", n)
