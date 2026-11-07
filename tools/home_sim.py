# -*- coding: utf-8 -*-
"""给家居板驱动加可选模拟模式（没硬件时也能演示界面）。"""
P = r"E:\zhikong\app\backend\devices\home_board.py"
s = open(P, encoding="utf-8").read()

# 1) 构造参数
s = s.replace(
    "    def __init__(self, port=None, baud=115200, on_event=None, log=print, poll=5.0):",
    "    def __init__(self, port=None, baud=115200, on_event=None, log=print, poll=5.0,\n"
    "                 sim=False):\n"
    "        self.sim = bool(sim)", 1)

# 2) sim 时不连串口，直接造数据
s = s.replace('''    def _loop(self):''',
'''    def _loop_sim(self):
        """模拟模式：按 10 秒节奏生成数据，便于无硬件演示。"""
        import random
        self.online = True
        self.firmware = "simulated"
        self.data.update({"temp": 26.5, "hum": 55.0, "lux": 180, "gas": 120,
                          "pir": 0, "light": 0, "fan": 0})
        n = 0
        while not self._stop:
            n += 1
            self.data["temp"] = round(self.data["temp"] + random.uniform(-0.15, 0.15), 1)
            self.data["hum"] = round(min(90, max(30, self.data["hum"] + random.uniform(-0.3, 0.3))), 1)
            self.data["lux"] = max(0, self.data["lux"] + random.randint(-8, 8))
            self.data["gas"] = max(30, self.data["gas"] + random.randint(-3, 3))
            if n % 6 == 0:
                before = self.data["pir"]
                self.data["pir"] = 0 if before else 1
                if self.on_event:
                    self.on_event({"type": "pir", "value": self.data["pir"]})
            time.sleep(10)
        return None

    def _loop(self):''', 1)

# 3) start 分流
s = s.replace('''        self._stop = False
        self._thread = threading.Thread(target=self._loop, name="home-board", daemon=True)''',
'''        self._stop = False
        target = self._loop_sim if self.sim else self._loop
        self._thread = threading.Thread(target=target, name="home-board", daemon=True)''', 1)

open(P, "w", encoding="utf-8").write(s)
print("模拟模式已加")

M = r"E:\zhikong\app\backend\main.py"
m = open(M, encoding="utf-8").read()
if 'home_sim' not in m:
    m = m.replace('self.home = HomeBoard(port=CONF["devices"].get("home_port"),\n                              log=log, on_event=self._on_home_event)',
                  'self.home = HomeBoard(port=CONF["devices"].get("home_port"), log=log,\n'
                  '                              on_event=self._on_home_event,\n'
                  '                              sim=bool(CONF["devices"].get("home_sim", False)))', 1)
    open(M, "w", encoding="utf-8").write(m)
    print("main.py 已支持 home_sim 配置")
