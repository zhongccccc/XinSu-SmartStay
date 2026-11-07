# -*- coding: utf-8 -*-
"""门锁板看门狗：掉线后每 15 秒重扫端口，回来就自动接管（不依赖 mock 状态）。"""
P = r"E:\zhikong\app\backend\devices\lock.py"
s = open(P, encoding="utf-8").read()

# 1) __init__ 末尾启动看门狗
OLD_INIT = """        else:
            self._use_mock = False

    def _scan_ports(self, baud):"""
NEW_INIT = """        else:
            self._use_mock = False
        # 常驻看门狗：掉线后自己找回来
        self._wd_stop = False
        threading.Thread(target=self._watchdog, daemon=True, name="lock-wd").start()

    def _watchdog(self):
        \"\"\"每 15 秒检查一次：板子不应答就重扫端口。\"\"\"
        while not getattr(self, "_wd_stop", False):
            time.sleep(15)
            try:
                if self._use_mock:
                    continue                      # mock 模式由 _reprobe 负责
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
                    self.log("[lock:wd] 门锁板已恢复（%s）%s" % (found, detail))
            except Exception as e:
                self.log("[lock:wd] 异常: %s" % e)

    def _scan_ports(self, baud):"""

if "_watchdog" not in s and OLD_INIT in s:
    s = s.replace(OLD_INIT, NEW_INIT, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("看门狗已加")
else:
    print("状态:", "已存在" if "_watchdog" in s else "未匹配")
