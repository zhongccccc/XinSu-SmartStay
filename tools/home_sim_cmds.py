# -*- coding: utf-8 -*-
"""模拟模式下 light/fan/beep 直接成功。"""
P = r"E:\zhikong\app\backend\devices\home_board.py"
s = open(P, encoding="utf-8").read()

s = s.replace('''    def light(self, on):
        ok = "ZH|ACK|LIGHT" in self.command("zh light %s" % ("on" if on else "off"), 2.0)''',
'''    def light(self, on):
        if self.sim:
            self.data["light"] = 1 if on else 0
            return True
        ok = "ZH|ACK|LIGHT" in self.command("zh light %s" % ("on" if on else "off"), 2.0)''', 1)

s = s.replace('''    def fan(self, duty):
        if isinstance(duty, bool):
            duty = 60 if duty else 0''',
'''    def fan(self, duty):
        if isinstance(duty, bool):
            duty = 60 if duty else 0
        if self.sim:
            self.data["fan"] = int(duty)
            return True''', 1)

s = s.replace('''    def beep(self, ms=150):
        return "ZH|ACK|BEEP" in self.command("zh beep %d" % int(ms), 2.5)''',
'''    def beep(self, ms=150):
        if self.sim:
            return True
        return "ZH|ACK|BEEP" in self.command("zh beep %d" % int(ms), 2.5)''', 1)

s = s.replace('''    def ping(self, wait=1.4):
        return "ZH|ACK|PING" in self.command("zh ping", wait)''',
'''    def ping(self, wait=1.4):
        if self.sim:
            return True
        return "ZH|ACK|PING" in self.command("zh ping", wait)''', 1)

open(P, "w", encoding="utf-8").write(s)
print("模拟模式命令已放行")
