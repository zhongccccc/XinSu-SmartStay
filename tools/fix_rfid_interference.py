# -*- coding: utf-8 -*-
"""删除读卡器对其它串口的干扰：不再扫描/占用门锁板和家居板的串口。

根因：_find_port() 会遍历所有 /dev/ttyUSB*，包括两块板子的端口，
     每 15 秒打开一次并往里写读卡命令，抢走了板子的串口数据。
"""
P = r"E:\zhikong\app\backend\devices\rfid_serial.py"
s = open(P, encoding="utf-8").read()

OLD = """            frames = self._transact()
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
            if not frames:
                self._idle += 1
                if self._idle > 100:            # 约 15 秒没有有效回包
                    self._idle = 0
                    if self._find_port():
                        self._close()
            else:
                self._idle = 0"""

NEW = """            frames = self._transact()
            # 注意：这里绝不能去扫描/打开其它串口（会抢走门锁板/家居板的数据）"""

if OLD in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("[OK] 已移除对其它串口的扫描")
else:
    print("!! 未匹配，需要手工检查")

# 双保险：_find_port 直接停用
if "def _find_port" in s:
    s = open(P, encoding="utf-8").read()
    s = s.replace("    def _find_port(self):",
                  "    def _find_port(self):\n        return None   # 已停用：不再扫描其它串口\n", 1)
    open(P, "w", encoding="utf-8").write(s)
    print("[OK] _find_port 已停用")
