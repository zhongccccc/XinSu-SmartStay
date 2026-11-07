# -*- coding: utf-8 -*-
"""开机认领加"重试等待"：给板子上电留出时间，尽量三个都认到。"""
P = r"E:\zhikong\app\backend\main.py"
s = open(P, encoding="utf-8").read()

OLD = '''    found = {}
    for p in sorted(_glob.glob("/dev/ttyUSB*")) + sorted(_glob.glob("/dev/ttyACM*")):'''

NEW = '''    found = {}
    # 板子上电需要时间：最多重试 8 轮（约 20 秒），直到 lock+home 都认到
    for _round in range(8):
        if "lock" in found and "home" in found:
            break
        if _round:
            time.sleep(2.5)
        for p in sorted(_glob.glob("/dev/ttyUSB*")) + sorted(_glob.glob("/dev/ttyACM*")):
            if p in (found.get("lock"), found.get("home")):
                continue
            _scan_one(p, found, log)
    return _finish_discovery(found, log)


def _scan_one(p, found, log):
    import select as _select
    import termios as _termios
    try:
        fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    except OSError:
        return
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

        _rd(0.25)
        os.write(fd, b"zk ping\\r")
        t = _rd(1.8)
        if b"ZK|ACK|PING" in t and "lock" not in found:
            found["lock"] = p
            log("[port] %s -> 门锁板" % p)
            return
        os.write(fd, b"zh ping\\r")
        t = _rd(1.8)
        if ("ZH|ACK|PING" in t or "[zh] alive" in t) and "home" not in found:
            found["home"] = p
            log("[port] %s -> 家居板" % p)
    except Exception as e:
        log("[port] 探测 %s 异常: %s" % (p, e))
    finally:
        try:
            os.close(fd)
        except OSError:
            pass


def _finish_discovery(found, log):
    import glob as _glob
    import select as _select
    import termios as _termios'''

if "_scan_one" not in s:
    s = s.replace(OLD, NEW, 1)
    print("[1] 已改为可重试的探测")
else:
    print("[1] 已存在")

open(P, "w", encoding="utf-8").write(s)
print("注意：需人工核对缩进是否正确")
