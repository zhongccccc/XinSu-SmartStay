# -*- coding: utf-8 -*-
"""去掉"60 秒无卡重开串口"（空闲时它会反复关/开读卡器，反而容易漏卡）。"""
P = r"E:\zhikong\app\backend\devices\rfid_serial.py"
s = open(P, encoding="utf-8").read()

OLD = """            frames = self._transact()
            # 注意：这里绝不能去扫描/打开其它串口（会抢走门锁板/家居板的数据）
            if frames:
                self._last_frame_ts = time.time()
            else:
                # 连续 60 秒没有任何有效帧 -> 关端口重开（相当于软件拔插）
                if time.time() - self._last_frame_ts > 60:
                    self.log("[rfid] 60 秒无卡，重开串口")
                    self._close()
                    self._last_frame_ts = time.time()
                    time.sleep(0.3)
                    continue"""

NEW = """            frames = self._transact()
            # 注意：这里绝不能扫描/打开其它串口（会抢走门锁板/家居板的数据），
            # 也不要空闲重开串口（会漏卡）。读卡器就老老实实一直轮询。"""

if OLD in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("[OK] 已去掉空闲重开")
else:
    print("未匹配，检查当前代码")
