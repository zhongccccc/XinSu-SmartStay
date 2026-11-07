# -*- coding: utf-8 -*-
P = r"E:\zhikong\app\backend\main.py"
s = open(P, encoding="utf-8").read()

CB = '''    def _on_home_event(self, ev):
        """家居板事件：人体 / 燃气。"""
        try:
            t = ev.get("type")
            if t == "pir":
                BUS.publish("home_pir", {"pir": ev.get("value")})
                log("[home] 人体感应 %s" % ("有人" if ev.get("value") else "无人"))
            elif t == "gas":
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

if "def _on_home_event" not in s:
    s = s.replace("    def start(self):", CB + "    def start(self):", 1)
    print("已插入 _on_home_event")
else:
    print("_on_home_event 已存在")

# 路由
ROUTES = '''            if p == "/api/home":
                st = APP.home.status()
                g = st.get("data", {}).get("gas") or 0
                st["alarm"] = bool(g > 2500)
                return self._json(st)
            if p == "/api/home/light":
                on = bool(self._body().get("on", True))
                ok = APP.home.light(on)
                return self._json({"ok": ok, "on": on})
            if p == "/api/home/fan":
                duty = int(self._body().get("duty", 60) or 0)
                ok = APP.home.fan(duty)
                return self._json({"ok": ok, "duty": duty})
            if p == "/api/home/beep":
                ok = APP.home.beep(int(self._body().get("ms", 150) or 150))
                return self._json({"ok": ok})
'''
if "/api/home/light" not in s:
    anchor = '            if p == "/api/checkout":'
    s = s.replace(anchor, ROUTES + anchor, 1)
    print("路由已加")

open(P, "w", encoding="utf-8").write(s)
