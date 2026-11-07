# -*- coding: utf-8 -*-
"""1) 家居板：配置了端口就只用这个端口，不再扫描（避免抢门锁板的串口）
2) 配置里固定 home_port
"""
P = r"E:\zhikong\app\backend\devices\home_board.py"
s = open(P, encoding="utf-8").read()

# 记录是否为固定端口
if "self._fixed_port" not in s:
    s = s.replace("        self.port = port\n        self.baud = baud",
                  "        self.port = port\n        self._fixed_port = bool(port)\n        self.baud = baud", 1)

OLD = '''        cand = [self.port] if self.port else []
        for p in sorted(glob.glob("/dev/ttyUSB*")) + sorted(glob.glob("/dev/ttyACM*")):
            if p not in cand:
                cand.append(p)'''
NEW = '''        if self._fixed_port and self.port:
            cand = [self.port]          # 固定端口：只探这一个，不打扰别的设备
        else:
            cand = list(sorted(glob.glob("/dev/ttyUSB*"))) + list(sorted(glob.glob("/dev/ttyACM*")))'''
if OLD in s:
    s = s.replace(OLD, NEW, 1)
    print("已改为固定端口")
elif "cand = [self.port]          # 固定端口" in s:
    print("已经是固定端口")
else:
    print("!! 未匹配 discover 候选逻辑")

open(P, "w", encoding="utf-8").write(s)
