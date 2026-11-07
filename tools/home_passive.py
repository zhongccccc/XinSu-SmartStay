# -*- coding: utf-8 -*-
"""把家居板驱动改成"被动监听优先"：解析板子自己的心跳，不再轮询轰炸。"""
P = r"E:\zhikong\app\backend\devices\home_board.py"
s = open(P, encoding="utf-8").read()

start = s.index("    def _loop(self):")
end = s.index("    def status(self):")

NEW = '''    def _loop(self):
        """被动监听板子的串口输出：

        固件每 10 秒打印一行心跳：
            [zh] alive #120 t=28.8 h=57.6 lux=112 gas=113 pir=0
        事件：
            ZH|EVT|PIR|1 / ZH|EVT|KEY|6 / ZH|EVT|LIGHT|off

        只有长时间没有心跳时才主动 ping 一次，避免把板子 shell 压垮。
        """
        last_rx = 0.0
        while not self._stop:
            try:
                if self._fd is None:
                    if not self.discover():
                        time.sleep(3.0)
                        continue
                    last_rx = time.time()

                chunk = self._read(0.6)
                if chunk:
                    last_rx = time.time()
                    self._buffer_text += chunk
                    # 按行切，保留最后半行
                    while "\\n" in self._buffer_text:
                        line, self._buffer_text = self._buffer_text.split("\\n", 1)
                        self._parse(line.strip("\\r "))

                # 30 秒没心跳 → 认为掉线，重连探测
                if time.time() - last_rx > 30:
                    self.log("[home] 30 秒无心跳，重新探测")
                    self.online = False
                    self._close()
                    last_rx = time.time()
            except Exception as e:
                self.last_error = str(e)
                self.log("[home] 监听异常: %s" % e)
                self._close()
                time.sleep(2.0)

    # 心跳格式： [zh] alive #120 t=28.8 h=57.6 lux=112 gas=113 pir=0
    _RE_ALIVE = re.compile(
        r"t=(-?[\\d.]+).*?h=(-?[\\d.]+).*?lux=(-?\\d+).*?gas=(-?\\d+).*?pir=(\\d)")

    def _parse(self, line):
        if not line:
            return
        if "alive" in line:
            m = self._RE_ALIVE.search(line)
            if m:
                before = dict(self.data)
                self.data["temp"] = float(m.group(1))
                self.data["hum"] = float(m.group(2))
                self.data["lux"] = int(m.group(3))
                self.data["gas"] = int(m.group(4))
                self.data["pir"] = int(m.group(5))
                self.online = True
                self.last_error = ""
                if self.data["pir"] != before.get("pir") and self.on_event:
                    self.on_event({"type": "pir", "value": self.data["pir"]})
                if self.data["gas"] != before.get("gas") and self.on_event:
                    self.on_event({"type": "gas", "value": self.data["gas"]})
            return

        if "ZH|EVT|" in line:
            m = re.search(r"ZH\\|EVT\\|(\\w+)\\|(\\S+)", line)
            if m:
                kind, val = m.group(1), m.group(2)
                if kind == "PIR":
                    self.data["pir"] = 1 if val == "1" else 0
                    if self.on_event:
                        self.on_event({"type": "pir", "value": self.data["pir"]})
                elif kind == "LIGHT":
                    self.data["light"] = 0 if val == "off" else 1
                elif kind == "KEY" and self.on_event:
                    self.on_event({"type": "key", "value": val})
            return

        if "ZH|ACK|ENV" in line:
            m = re.search(r"t=(-?[\\d.]+)\\|h=(-?[\\d.]+)\\|lux=(-?\\d+)", line)
            if m:
                self.data["temp"] = float(m.group(1))
                self.data["hum"] = float(m.group(2))
                self.data["lux"] = int(m.group(3))
                self.online = True

'''
s = s[:start] + NEW + s[end:]

# 增加缓冲字段
s = s.replace("        self._buf = b\"\"", "        self._buf = b\"\"\n        self._buffer_text = \"\"", 1)

open(P, "w", encoding="utf-8").write(s)
print("驱动已改为被动监听")
