# -*- coding: utf-8 -*-
"""修 discover：ping 不通的端口不要占住。"""
P = r"E:\zhikong\app\backend\devices\home_board.py"
s = open(P, encoding="utf-8").read()

OLD = '''    def _open(self, port):
        try:
            self._fd = _open_serial(port, self.baud)
            self.port = port
            self._buf = b""
            return True'''
NEW = '''    def _open(self, port):
        try:
            self._fd = _open_serial(port, self.baud)
            self._buf = b""
            return True'''
n = 0
if OLD in s:
    s = s.replace(OLD, NEW, 1); n += 1

OLD2 = '''            if "ZH|ACK|PING" in text:
                m = re.search(r"ZH\\|ACK\\|PING\\|OK\\|([^|\\r\\n]+)", text)
                self.firmware = m.group(1).strip() if m else None
                self.online = True
                self.last_error = ""
                self.log("[home] 找到板子 %s %s" % (port, self.firmware or ""))
                return True
            self._close()
        self.online = False
        self.last_error = "未找到 zh 板子"
        return False'''
NEW2 = '''            if "ZH|ACK|PING" in text:
                m = re.search(r"ZH\\|ACK\\|PING\\|OK\\|([^|\\r\\n]+)", text)
                self.firmware = m.group(1).strip() if m else None
                self.port = port
                self.online = True
                self.last_error = ""
                self.log("[home] 找到板子 %s %s" % (port, self.firmware or ""))
                return True
            self._close()
        self.online = False
        self.port = None
        self.last_error = "未找到 zh 板子"
        return False'''
if OLD2 in s:
    s = s.replace(OLD2, NEW2, 1); n += 1

open(P, "w", encoding="utf-8").write(s)
print("替换:", n)
