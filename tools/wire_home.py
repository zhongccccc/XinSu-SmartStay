# -*- coding: utf-8 -*-
"""把智能家居板接入系统。"""
P = r"E:\zhikong\app\backend\main.py"
s = open(P, encoding="utf-8").read()

# 1) import
if "from devices.home_board import HomeBoard" not in s:
    s = s.replace("from devices.lock import build_lock",
                  "from devices.home_board import HomeBoard\nfrom devices.lock import build_lock", 1)

# 2) 实例化（放在 ctrl 之后，便于回调里用 ctrl）
old = "        self.ctrl = Controller(self.db, self.registry, self.audio, self.lock)"
new = """        self.ctrl = Controller(self.db, self.registry, self.audio, self.lock)
        self.home = HomeBoard(port=CONF["devices"].get("home_port"),
                              log=log, on_event=self._on_home_event)
        self._home_alarm_at = 0.0"""
if old in s:
    s = s.replace(old, new, 1)

# 3) 事件回调
anchor = "    def start(self):"
cb = '''    def _on_home_event(self, ev):
        """家居板事件：人体 / 燃气。"""
        try:
            if ev.get("type") == "pir":
                BUS.publish("home_pir", {"pir": ev.get("value")})
                log("[home] 人体感应 %s" % ("有人" if ev.get("value") else "无人"))
            elif ev.get("type") == "gas":
                gas = int(ev.get("value") or 0)
                BUS.publish("home_gas", {"gas": gas, "alarm": gas > 2500})
                if gas > 2500 and time.time() - self._home_alarm_at > 120:
                    self._home_alarm_at = time.time()
                    try:
                        wid = self.db.create_workorder(
                            (self.ctrl.state.get("room") or {}).get("no") or "-",
                            "燃气浓度超标（%d），请立即检查" % gas, "alarm")
                    except Exception:
                        wid = None
                    BUS.publish("home_alarm", {"gas": gas, "workorder": wid})
                    self.audio.say("警告，客房燃气浓度超标，请立即检查")
        except Exception as e:
            log("[home] 事件处理异常: %s" % e)

'''
if "_on_home_event" not in s.split("def start(self):")[0]:
    s = s.replace(anchor, cb + anchor, 1)

# 4) 启动时拉起
s = s.replace("        if self.rfid:\n            self.rfid.start()",
              "        if self.rfid:\n            self.rfid.start()\n        self.home.start()", 1)

# 5) health 里加家居板
s = s.replace('"camera": APP.camera.info(), "lock": APP.lock.status(),',
              '"camera": APP.camera.info(), "lock": APP.lock.status(),\n                 "home": APP.home.status(),', 1)

open(P, "w", encoding="utf-8").write(s)
print("main.py 已接入家居板")
