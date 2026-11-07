# -*- coding: utf-8 -*-
"""摄像头卡死保护：帧过期时主动重开管线，快照不再无限等待。"""
P = r"E:\zhikong\app\backend\devices\camera.py"
s = open(P, encoding="utf-8").read()

# 1) 记录帧时间戳
if "self.last_ts" not in s:
    s = s.replace("            self.last_frame = frame",
                  "            self.last_frame = frame\n            self.last_ts = time.time()", 1)

# 2) 新鲜度判断 + 等待
if "def frame_age" not in s:
    s = s.replace("    # ---------- 对外 ----------",
'''    # ---------- 对外 ----------
    def frame_age(self):
        """最后一帧距今多少秒；没有帧返回一个很大的数。"""
        ts = getattr(self, "last_ts", 0)
        if not ts or self.last_frame is None:
            return 999.0
        return max(0.0, time.time() - ts)

    def wait_fresh(self, max_age=2.0, timeout=3.0):
        """等一帧新鲜的；超时返回 False。"""
        end = time.time() + timeout
        while time.time() < end:
            if self.frame_age() <= max_age:
                return True
            time.sleep(0.15)
        return False
''', 1)

# 3) snapshot 在帧过期时先重开管线
OLD_SNAP = '''    def snapshot(self, path):
        data = self.jpeg(960, 88)'''
NEW_SNAP = '''    def snapshot(self, path):
        # 帧过期说明管线卡住了：先重开，再等最多 3 秒
        if self.frame_age() > 2.0:
            self.log("[camera] 画面已过期 %.1fs，重开管线" % self.frame_age())
            try:
                self._reopen()
            except Exception as e:
                self.log("[camera] 重开失败: %s" % e)
            if not self.wait_fresh(1.0, 3.0):
                self.log("[camera] 重开后仍无画面，返回失败")
                return None
        data = self.jpeg(960, 88)'''
if OLD_SNAP in s:
    s = s.replace(OLD_SNAP, NEW_SNAP, 1)
    print("snapshot 已加保护")

open(P, "w", encoding="utf-8").write(s)
print("camera.py 已更新")
