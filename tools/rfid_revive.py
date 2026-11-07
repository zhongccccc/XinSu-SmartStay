# -*- coding: utf-8 -*-
"""读卡器自动复活：连续 60 秒读不到卡就关端口重开，模拟一次"拔插"。"""
P = r"E:\zhikong\app\backend\devices\rfid_serial.py"
s = open(P, encoding="utf-8").read()

# 1) 记录最近一次有效帧时间
if "self._last_frame_ts" not in s:
    s = s.replace("        self._idle = 0\n",
                  "        self._idle = 0\n"
                  "        self._last_frame_ts = time.time()\n", 1)

# 2) 主循环里：读到帧就更新时间；长时间没帧就重开
OLD = """            frames = self._transact()
            if not frames:"""
NEW = """            frames = self._transact()
            if frames:
                self._last_frame_ts = time.time()
            else:
                # 连续 60 秒没有任何有效帧 -> 关端口重开（相当于软件拔插）
                if time.time() - self._last_frame_ts > 60:
                    self.log("[rfid] 60 秒无卡，重开串口")
                    self._close()
                    self._last_frame_ts = time.time()
                    self._find_port()
                    time.sleep(0.3)
                    continue
            if not frames:"""

if OLD in s and "60 秒无卡" not in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("已加读卡器自动复活")
else:
    print("状态:", "已存在" if "60 秒无卡" in s else "未匹配")
