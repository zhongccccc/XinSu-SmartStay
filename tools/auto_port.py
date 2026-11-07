# -*- coding: utf-8 -*-
"""开机时扫一遍串口，按协议认领：门锁板(ZK) / 家居板(ZH)，其余留给读卡器。
这样端口号随插拔变化也不影响。
"""
P = r"E:\zhikong\app\backend\main.py"
s = open(P, encoding="utf-8").read()

DISCOVER = '''def discover_serial_ports(log=print):
    """开机扫一次串口，按协议认领设备端口。

    返回 {"lock": "/dev/ttyUSBx", "home": "/dev/ttyUSBx"}
    """
    import glob as _glob
    import select as _select
    import termios as _termios

    found = {}
    for p in sorted(_glob.glob("/dev/ttyUSB*")) + sorted(_glob.glob("/dev/ttyACM*")):
        try:
            fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        except OSError:
            continue
        try:
            a = _termios.tcgetattr(fd)
            a[0] = a[1] = 0
            a[2] = (a[2] & ~_termios.CSIZE) | _termios.CS8
            a[2] &= ~(_termios.PARENB | _termios.CSTOPB | _termios.CRTSCTS)
            a[3] = 0
            a[4] = a[5] = _termios.B115200
            a[6][_termios.VMIN] = 0
            a[6][_termios.VTIME] = 0
            _termios.tcsetattr(fd, _termios.TCSANOW, a)

            def _rd(sec):
                b = b""
                end = time.time() + sec
                while time.time() < end:
                    r, _, _ = _select.select([fd], [], [], 0.1)
                    if r:
                        try:
                            b += os.read(fd, 512)
                        except BlockingIOError:
                            pass
                return b

            _rd(0.3)
            os.write(fd, b"zk ping\\r")
            t = _rd(1.6)
            if b"ZK|ACK|PING" in t:
                found["lock"] = p
                log("[port] %s -> 门锁板" % p)
            else:
                os.write(fd, b"zh ping\\r")
                t = _rd(1.6)
                if b"ZH|ACK|PING" in t:
                    found["home"] = p
                    log("[port] %s -> 家居板" % p)
        except Exception as e:
            log("[port] 探测 %s 异常: %s" % (p, e))
        finally:
            try:
                os.close(fd)
            except OSError:
                pass
        if "lock" in found and "home" in found:
            break
    return found


'''

if "def discover_serial_ports" not in s:
    anchor = "class App:"
    idx = s.find(anchor)
    if idx > 0:
        s = s[:idx] + DISCOVER + s[idx:]
        print("已加入端口自动认领函数")

# 在 App.__init__ 里先认领端口
OLD = '''        self.lock = build_lock(CONF["devices"], self.db, log,
                              on_event=self._on_lock_event)'''
NEW = '''        _ports = discover_serial_ports(log)
        _dev = dict(CONF["devices"])
        _dev["lock"] = dict(_dev.get("lock") or {})
        if _ports.get("lock"):
            _dev["lock"]["port"] = _ports["lock"]
        _home_port = _ports.get("home") or _dev.get("home_port")
        self.lock = build_lock(_dev, self.db, log,
                              on_event=self._on_lock_event)'''
if OLD in s:
    s = s.replace(OLD, NEW, 1)
    print("已接入端口认领（门锁板）")

s = s.replace('self.home = HomeBoard(port=CONF["devices"].get("home_port"), log=log,',
              'self.home = HomeBoard(port=_home_port, log=log,', 1)

open(P, "w", encoding="utf-8").write(s)
print("main.py 已更新")
