# -*- coding: utf-8 -*-
"""修正：自动找端口必须校验是合法读卡帧，避免误认门锁板/家居板的串口。"""
P = r"E:\zhikong\app\backend\devices\rfid_serial.py"
s = open(P, encoding="utf-8").read()

OLD = '''                if len(buf) >= 5:
                    self.log("[rfid] 在 %s 发现读卡器" % p)
                    self.port = p
                    return p'''
NEW = '''                frames = scan_frames(buf) if buf else []
                if frames and any(len(f) >= 12 for f in frames):
                    self.log("[rfid] 在 %s 发现读卡器" % p)
                    self.port = p
                    return p'''
if OLD in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("已改为校验合法帧")
else:
    print("未匹配")
