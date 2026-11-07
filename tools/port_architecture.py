# -*- coding: utf-8 -*-
"""串口架构改造：开机认领一次（lock/home/rfid），之后任何驱动都不再扫描串口。

这是解决"一块板掉线就互相拖死"的根本改动。
"""
P = r"E:\zhikong\app\backend\main.py"
s = open(P, encoding="utf-8").read()

# ---------- 1) discover_serial_ports 增加读卡器识别 ----------
OLD_END = '''        if "lock" in found and "home" in found:
            break
    return found'''

NEW_END = '''        if "lock" in found and "home" in found:
            break

    # 认领读卡器：剩下的串口里，谁能回合法读卡帧就是它
    try:
        from .devices.rfid_serial import CMD_READ_ID, scan_frames
        for p in sorted(_glob.glob("/dev/ttyUSB*")) + sorted(_glob.glob("/dev/ttyACM*")):
            if p in (found.get("lock"), found.get("home")):
                continue
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
                a[4] = a[5] = _termios.B9600
                a[6][_termios.VMIN] = 0
                a[6][_termios.VTIME] = 0
                _termios.tcsetattr(fd, _termios.TCSANOW, a)
                for _ in range(3):
                    try:
                        while os.read(fd, 512):
                            pass
                    except BlockingIOError:
                        pass
                    os.write(fd, CMD_READ_ID)
                    t0 = time.time()
                    buf = b""
                    while time.time() - t0 < 0.35:
                        r, _, _ = _select.select([fd], [], [], 0.05)
                        if r:
                            try:
                                buf += os.read(fd, 256)
                            except BlockingIOError:
                                pass
                    fr = scan_frames(buf) if buf else []
                    if fr and any(len(f) >= 12 for f in fr):
                        found["rfid"] = p
                        log("[port] %s -> 读卡器" % p)
                        break
                    time.sleep(0.1)
            finally:
                try:
                    os.close(fd)
                except OSError:
                    pass
            if "rfid" in found:
                break
    except Exception as e:
        log("[port] 读卡器识别失败: %s" % e)

    return found'''

if 'found["rfid"]' not in s and OLD_END in s:
    s = s.replace(OLD_END, NEW_END, 1)
    print("[1] 读卡器识别已加")
else:
    print("[1] 状态:", "已存在" if 'found["rfid"]' in s else "未匹配")

# ---------- 2) 门锁板：用认领到的端口，硬失败不扫描 ----------
OLD_LOCK = '''        _ports = discover_serial_ports(log)
        _dev = dict(CONF["devices"])
        _dev["lock"] = dict(_dev.get("lock") or {})
        if _ports.get("lock"):
            _dev["lock"]["port"] = _ports["lock"]
        _home_port = _ports.get("home") or _dev.get("home_port")'''
NEW_LOCK = '''        _ports = discover_serial_ports(log)
        _dev = dict(CONF["devices"])
        _dev["lock"] = dict(_dev.get("lock") or {})
        if _ports.get("lock"):
            _dev["lock"]["port"] = _ports["lock"]
        _dev["lock"]["transport"] = "board"      # 固定端口，不再扫描
        _home_port = _ports.get("home") or _dev.get("home_port")
        _rfid_port = _ports.get("rfid")
        if _rfid_port:
            CONF.setdefault("rfid", {})["port"] = _rfid_port'''

if "固定端口，不再扫描" not in s and OLD_LOCK in s:
    s = s.replace(OLD_LOCK, NEW_LOCK, 1)
    print("[2] 门锁板改为固定端口")
else:
    print("[2] 状态:", "已存在" if "固定端口，不再扫描" in s else "未匹配")

open(P, "w", encoding="utf-8").write(s)
print("done")
