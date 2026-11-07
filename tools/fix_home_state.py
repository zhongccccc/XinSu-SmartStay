# -*- coding: utf-8 -*-
P = r"E:\zhikong\app\backend\devices\home_board.py"
s = open(P, encoding="utf-8").read()

OLD_LIGHT = '''    def light(self, on):
        return "ZH|ACK|LIGHT" in self.command("zh light %s" % ("on" if on else "off"), 2.0)
'''
NEW_LIGHT = '''    def light(self, on):
        ok = "ZH|ACK|LIGHT" in self.command("zh light %s" % ("on" if on else "off"), 2.0)
        if ok:
            self.data["light"] = 1 if on else 0
        return ok
'''
OLD_FAN = '''    def fan(self, duty):
        if isinstance(duty, bool):
            duty = 60 if duty else 0
        return "ZH|ACK|FAN" in self.command("zh fan %d" % int(duty), 2.0)
'''
NEW_FAN = '''    def fan(self, duty):
        if isinstance(duty, bool):
            duty = 60 if duty else 0
        ok = "ZH|ACK|FAN" in self.command("zh fan %d" % int(duty), 2.0)
        if ok:
            self.data["fan"] = int(duty)
        return ok
'''
n = 0
if OLD_LIGHT in s:
    s = s.replace(OLD_LIGHT, NEW_LIGHT, 1); n += 1
if OLD_FAN in s:
    s = s.replace(OLD_FAN, NEW_FAN, 1); n += 1
open(P, "w", encoding="utf-8").write(s)
print("替换:", n)
