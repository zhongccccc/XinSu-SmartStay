# -*- coding: utf-8 -*-
"""家居板发现：ping 不通时，只要收到心跳/事件也算认领（shell 挂了也能连）。"""
P = r"E:\zhikong\app\backend\devices\home_board.py"
s = open(P, encoding="utf-8").read()

OLD = """            if "ZH|ACK|PING" in text:
                m = re.search(r"ZH\\|ACK\\|PING\\|OK\\|([^|\\r\\n]+)", text)
                self.firmware = m.group(1).strip() if m else None
                self.port = port
                self.online = True
                self.last_error = ""
                self.log("[home] 找到板子 %s %s" % (port, self.firmware or ""))
                return True
            self._close()"""

NEW = """            # ping 没回应时：板子若在自发心跳/事件，也认（应用活着但 shell 可能挂了）
            if "ZH|ACK|PING" not in text:
                text += self._read(3.5)
            if ("ZH|ACK|PING" in text) or ("[zh] alive" in text) or ("ZH|EVT|" in text):
                m = re.search(r"ZH\\|ACK\\|PING\\|OK\\|([^|\\r\\n]+)", text)
                self.firmware = m.group(1).strip() if m else "heartbeat"
                self.port = port
                self.online = True
                self.last_error = ""
                self.log("[home] 找到板子 %s (%s)" % (port, self.firmware))
                return True
            self._close()"""

if OLD in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("OK: 已改为心跳也能认领")
else:
    print("!! 未匹配")
