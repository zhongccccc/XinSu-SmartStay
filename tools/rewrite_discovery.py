# -*- coding: utf-8 -*-
"""用一份干净实现替换 discover_serial_ports。

原则：
  1. 只在开机时探测一次（可重试等待板子上电）
  2. 认领后各驱动只用自己那一个端口，运行期谁都不许再扫描
"""
P = r"E:\zhikong\app\backend\main.py"
s = open(P, encoding="utf-8").read()

start = s.index("def discover_serial_ports(log=print):")
end = s.index("class App:")

NEW = '''def _probe_port(p, log):
    """返回 'lock' / 'home' / None"""
    import select as _sel
    import termios as _tm
    try:
        fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    except OSError:
        return None
    try:
        a = _tm.tcgetattr(fd)
        a[0] = a[1] = 0
        a[2] = (a[2] & ~_tm.CSIZE) | _tm.CS8
        a[2] &= ~(_tm.PARENB | _tm.CSTOPB | _tm.CRTSCTS)
        a[3] = 0
        a[4] = a[5] = _tm.B115200
        a[6][_tm.VMIN] = 0
        a[6][_tm.VTIME] = 0
        _tm.tcsetattr(fd, _tm.TCSANOW, a)

        def rd(sec):
            b = b""
            end = time.time() + sec
            while time.time() < end:
                r, _, _ = _sel.select([fd], [], [], 0.1)
                if r:
                    try:
                        b += os.read(fd, 512)
                    except BlockingIOError:
                        pass
            return b

        rd(0.25)
        os.write(fd, b"zk ping\\r")
        t = rd(1.8)
        if b"ZK|ACK|PING" in t:
            return "lock"
        os.write(fd, b"zh ping\\r")
        t = rd(1.8)
        if b"ZH|ACK|PING" in t or b"[zh] alive" in t:
            return "home"
        return None
    finally:
        try:
            os.close(fd)
        except OSError:
            pass


def _probe_rfid(p):
    """用读卡命令识别读卡器"""
    import select as _sel
    import termios as _tm
    try:
        from .devices.rfid_serial import CMD_READ_ID, scan_frames
    except Exception:
        return False
    try:
        fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    except OSError:
        return False
    try:
        a = _tm.tcgetattr(fd)
        a[0] = a[1] = 0
        a[2] = (a[2] & ~_tm.CSIZE) | _tm.CS8
        a[2] &= ~(_tm.PARENB | _tm.CSTOPB | _tm.CRTSCTS)
        a[3] = 0
        a[4] = a[5] = _tm.B9600
        a[6][_tm.VMIN] = 0
        a[6][_tm.VTIME] = 0
        _tm.tcsetattr(fd, _tm.TCSANOW, a)
        for _ in range(4):
            try:
                while os.read(fd, 512):
                    pass
            except BlockingIOError:
                pass
            os.write(fd, CMD_READ_ID)
            buf = b""
            end = time.time() + 0.35
            while time.time() < end:
                r, _, _ = _sel.select([fd], [], [], 0.05)
                if r:
                    try:
                        buf += os.read(fd, 256)
                    except BlockingIOError:
                        pass
            fr = scan_frames(buf) if buf else []
            if fr and any(len(f) >= 12 for f in fr):
                return True
            time.sleep(0.1)
        return False
    finally:
        try:
            os.close(fd)
        except OSError:
            pass


def discover_serial_ports(log=print):
    """开机认领设备端口，最多重试约 20 秒（等板子上电）。

    返回 {"lock": "...", "home": "...", "rfid": "..."}
    """
    import glob as _glob

    ports = sorted(_glob.glob("/dev/ttyUSB*")) + sorted(_glob.glob("/dev/ttyACM*"))
    found = {}
    for rnd in range(6):
        if "lock" in found and "home" in found:
            break
        if rnd:
            time.sleep(2.0)
        for p in ports:
            if p in (found.get("lock"), found.get("home")):
                continue
            kind = _probe_port(p, log)
            if kind and kind not in found:
                found[kind] = p
                log("[port] %s -> %s" % (p, "门锁板" if kind == "lock" else "家居板"))

    # 剩下的端口里找读卡器
    for p in ports:
        if p in found.values():
            continue
        if _probe_rfid(p):
            found["rfid"] = p
            log("[port] %s -> 读卡器" % p)
            break

    log("[port] 认领结果: %s" % found)
    return found


'''

s = s[:start] + NEW + s[end:]
open(P, "w", encoding="utf-8").write(s)
print("已替换 discover_serial_ports")
