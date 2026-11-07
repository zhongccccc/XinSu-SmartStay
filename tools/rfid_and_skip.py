# -*- coding: utf-8 -*-
"""1) 读卡器自动找端口（端口号变了也能自己找到）
2) 房卡步骤 20 秒无卡自动跳过（不阻塞入住）
"""
# ---------- 1) rfid 自动端口 ----------
P = r"E:\zhikong\app\backend\devices\rfid_serial.py"
s = open(P, encoding="utf-8").read()

if "_find_port" not in s:
    OLD_OPEN = '''    def _open(self):'''
    NEW_OPEN = '''    def _find_port(self):
        """遍历串口，发一次读卡命令，谁回包用谁。"""
        import glob as _glob
        for p in sorted(_glob.glob("/dev/ttyUSB*")) + sorted(_glob.glob("/dev/ttyACM*")):
            if p == self.port:
                continue
            try:
                fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
            except OSError:
                continue
            try:
                a = termios.tcgetattr(fd)
                a[0] = a[1] = 0
                a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
                a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
                a[3] = 0
                a[4] = a[5] = SPEEDS.get(self.baud, termios.B9600)
                a[6][termios.VMIN] = 0
                a[6][termios.VTIME] = 0
                termios.tcsetattr(fd, termios.TCSANOW, a)
                try:
                    while os.read(fd, 1024):
                        pass
                except BlockingIOError:
                    pass
                os.write(fd, CMD_READ_ID)
                buf = b""
                end = time.time() + 0.4
                while time.time() < end:
                    r, _, _ = select.select([fd], [], [], 0.05)
                    if r:
                        try:
                            buf += os.read(fd, 256)
                        except (BlockingIOError, OSError):
                            break
                if len(buf) >= 5:
                    self.log("[rfid] 在 %s 发现读卡器" % p)
                    self.port = p
                    return p
            except Exception:
                pass
            finally:
                try:
                    os.close(fd)
                except OSError:
                    pass
        return None

    def _open(self):'''
    if OLD_OPEN in s:
        s = s.replace(OLD_OPEN, NEW_OPEN, 1)

    # 主循环：连续无卡 15 秒就重新找端口
    OLD_LOOP = '''            frames = self._transact()'''
    NEW_LOOP = '''            frames = self._transact()
            if not frames:
                self._idle += 1
                if self._idle > 100:            # 约 15 秒没有有效回包
                    self._idle = 0
                    if self._find_port():
                        self._close()
            else:
                self._idle = 0'''
    if OLD_LOOP in s:
        s = s.replace(OLD_LOOP, NEW_LOOP, 1)

    # 计数器
    s = s.replace("        self.reads = 0\n", "        self.reads = 0\n        self._idle = 0\n", 1)
    open(P, "w", encoding="utf-8").write(s)
    print("rfid: 自动找端口已加")

# ---------- 2) 房卡步骤超时自动跳过 ----------
M = r"E:\zhikong\app\backend\core\model.py"
m = open(M, encoding="utf-8").read()

if "_card_timeout" not in m:
    # 进入 card 步骤时起一个定时线程
    OLD_GOTO = '''        self._say("支付成功，请将房卡放在读卡区为您写卡")
        return self._goto("card", "支付成功，请将房卡放在读卡区", card_uid=None)'''
    NEW_GOTO = '''        self._say("支付成功，请将房卡放在读卡区为您写卡")
        snap = self._goto("card", "支付成功，请将房卡放在读卡区", card_uid=None)
        threading.Thread(target=self._card_skip_after, args=(20,),
                         daemon=True, name="card-timeout").start()
        return snap'''
    if OLD_GOTO in m:
        m = m.replace(OLD_GOTO, NEW_GOTO, 1)

    HELPER = '''    def _card_skip_after(self, seconds):
        """房卡步骤超时自动放行（读卡器无响应时不阻塞入住）。"""
        time.sleep(seconds)
        with self._lk:
            if self.state["step"] != "card":
                return
        self.on_card("-")

'''
    if "def _card_skip_after" not in m:
        anchor = "    def on_card(self, uid):"
        m = m.replace(anchor, HELPER + anchor, 1)
    open(M, "w", encoding="utf-8").write(m)
    print("model: 房卡超时自动跳过已加")
