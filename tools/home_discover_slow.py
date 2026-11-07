# -*- coding: utf-8 -*-
"""家居板探测：每个端口重试两次、每次等更久，避免板子忙时漏应答。"""
P = r"E:\zhikong\app\backend\devices\home_board.py"
s = open(P, encoding="utf-8").read()

OLD = '''            # 丢掉残留
            self._read(0.2)
            if not self._write("zh ping"):
                continue
            text = self._read(1.4)
            if "ZH|ACK|PING" in text:'''

NEW = '''            # 丢掉残留
            self._read(0.3)
            text = ""
            for _try in range(2):
                if not self._write("zh ping"):
                    break
                text = self._read(2.2)
                if "ZH|ACK|PING" in text:
                    break
            if "ZH|ACK|PING" in text:'''

if OLD in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("探测已加长并重试")
else:
    print("未匹配")
