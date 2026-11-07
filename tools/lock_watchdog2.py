# -*- coding: utf-8 -*-
P = r"E:\zhikong\app\backend\devices\lock.py"
s = open(P, encoding="utf-8").read()

OLD = """            else:
                self._use_mock = False

    def _scan_ports(self, baud):"""

NEW = """            else:
                self._use_mock = False
        self._wd_stop = False
        threading.Thread(target=self._watchdog, daemon=True, name="lock-wd").start()

    def _watchdog(self):
        \"\"\"每 15 秒探一次；掉线就重扫端口，回来自动接管。\"\"\"
        while not getattr(self, "_wd_stop", False):
            time.sleep(15)
            try:
                if self._use_mock:
                    continue
                ok, _ = self._board.ping(1.0)
                if ok:
                    continue
                self.log("[lock:wd] 板子无应答，重扫端口")
                found = self._scan_ports(self.baud)
                if not found:
                    continue
                from .lock_board import BoardLock
                self.port = found
                self._board = BoardLock(found, self.baud, on_event=self._on_evt, log=self.log)
                ok2, detail = self._board.ping(1.5)
                if ok2:
                    self.log("[lock:wd] 已恢复（%s）%s" % (found, detail))
            except Exception as e:
                self.log("[lock:wd] 异常: %s" % e)

    def _scan_ports(self, baud):"""

if "_watchdog" not in s and OLD in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("看门狗已加")
else:
    print("状态:", "已存在" if "_watchdog" in s else "未匹配")
