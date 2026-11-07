# -*- coding: utf-8 -*-
"""读卡器兜底：探测不出来时，用剩下的那个串口（三个设备三个口，剩下的一定是它）。"""
P = r"E:\zhikong\app\backend\main.py"
s = open(P, encoding="utf-8").read()

OLD = '''    log("[port] 认领结果: %s" % found)
    return found'''
NEW = '''    if "rfid" not in found:
        rest = [p for p in ports if p not in found.values()]
        if len(rest) == 1:
            found["rfid"] = rest[0]
            log("[port] %s -> 读卡器（按排除法）" % rest[0])

    log("[port] 认领结果: %s" % found)
    return found'''

if "按排除法" not in s and OLD in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("已加排除法兜底")
else:
    print("状态:", "已存在" if "按排除法" in s else "未匹配")
