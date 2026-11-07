# -*- coding: utf-8 -*-
"""芯宿·智控 —— K1 边缘网关 / 自助入住一体机 后端入口。

启动： cd /opt/zhikong/app && python3 -m backend.main
"""
import json
import mimetypes
import os
import posixpath
import subprocess
import sys
import threading
import time
import traceback
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .config import ASSET_DIR, CONF, WEB_DIR, VOICE_DIR
from .core.bus import BUS, sse_format
from .core.db import DB
from .core.model import Controller
from .devices.audio import Audio
from .devices.camera import Camera
from .devices.home_board import HomeBoard
from .devices.idcard import IdCardReader
from .devices.idcard_web import IdCardWebApi
from .devices.face_local import LocalFaceVerifier
from .devices.rfid_serial import SerialRfid
from .devices.lock import build_lock
from .devices.registry import DeviceRegistry
from .devices.scanner import ScannerHub

LOG_FILE = os.path.join(os.environ.get("ZHIKONG_HOME", "/opt/zhikong"), "logs", "backend.log")


def log(msg):
    line = "%s %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def _probe_port(p, log):
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
        os.write(fd, b"zk ping\r")
        t = rd(1.8)
        if b"ZK|ACK|PING" in t:
            return "lock"
        os.write(fd, b"zh ping\r")
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

    if "rfid" not in found:
        rest = [p for p in ports if p not in found.values()]
        if len(rest) == 1:
            found["rfid"] = rest[0]
            log("[port] %s -> 读卡器（按排除法）" % rest[0])

    log("[port] 认领结果: %s" % found)
    return found


class App:
    def __init__(self):
        self.db = DB()
        self.audio = Audio(log)
        self.camera = Camera(CONF["devices"].get("camera_exclude_name_re", ""), log,
                             pipeline=CONF.get("camera", {}).get("pipeline", ""),
                             cfg_path=CONF.get("camera", {}).get("config", ""))
        if CONF["devices"].get("camera_disabled"):
            log("[camera] 已按配置停用（人脸为自动放行，不需要摄像头）")
        else:
            self.camera.probe()
        _ports = discover_serial_ports(log)
        _dev = dict(CONF["devices"])
        _dev["lock"] = dict(_dev.get("lock") or {})
        if _ports.get("lock"):
            _dev["lock"]["port"] = _ports["lock"]
        _dev["lock"]["transport"] = "board"      # 固定端口，不再扫描
        _home_port = _ports.get("home") or _dev.get("home_port") or "/dev/ttyUSB2"
        _rfid_port = _ports.get("rfid")
        if _rfid_port:
            CONF.setdefault("rfid", {})["port"] = _rfid_port
        self.lock = build_lock(_dev, self.db, log,
                               on_event=self._on_lock_event)
        self.scanner = ScannerHub(self._on_scan,
                                  name_re=CONF["devices"].get("scanner_name_re", ""), log=log)
        self.registry = DeviceRegistry(self.camera, self.audio, self.lock, self.scanner,
                                       rfid=getattr(self, "rfid", None))
        self.ctrl = Controller(self.db, self.registry, self.audio, self.lock)
        self.home = HomeBoard(port=_home_port, log=log,
                              on_event=self._on_home_event,
                              sim=bool(CONF["devices"].get("home_sim", False)))
        self._home_alarm_at = 0.0
        self.ctrl.attach_home(self.home)
        # 本机人脸比对（模型在 /opt/zhikong/face）
        self.face = LocalFaceVerifier(log=log)
        if self.face.available():
            threading.Thread(target=self.face.warmup, daemon=True, name="face-warmup").start()
            log("[face] 比对模块就绪（后台预热中）")
        else:
            log("[face] 未找到 /opt/zhikong/face，人脸核验将不可用")

        self.idcard = IdCardReader(self._on_idcard, log)
        idc = CONF.get("idcard", {})
        self.idcard_web = None
        if idc.get("mode", "auto") in ("auto", "webapi"):
            self.idcard_web = IdCardWebApi(self._on_idcard,
                                           idc.get("url", "http://127.0.0.1:7846"),
                                           idc.get("interval", 1.5),
                                           timeout=float(idc.get("timeout", 15)), log=log)

        rfc = CONF.get("rfid", {})
        self.rfid = None
        if rfc.get("transport", "serial") == "serial" and rfc.get("enabled", True):
            self.rfid = SerialRfid(self._on_rfid, rfc.get("port", "/dev/ttyUSB0"),
                                   rfc.get("baud", 9600), log=log)
        self.registry.rfid = self.rfid

    def _on_rfid(self, uid, card_type):
        """串口 RFID 读到卡：总线广播 + 审计 + 在「房卡」步骤推进流程。"""
        step = self.ctrl.state["step"]
        data = {"code": uid, "kind": "rfid", "device": "serial-rfid",
                "card_type": card_type, "step": step}
        self.db.audit("scan", data)
        BUS.publish("scan", data)
        if step == "card":
            self.ctrl.on_card(uid)
        elif step == "idle":
            # 待机时刷卡 = 刷房卡退房（用最初接入的 USB 读卡器）
            self.ctrl.on_card(uid)
            lc = getattr(self.ctrl, "last_card", None)
            if lc and lc.get("mode") == "checkout" and (lc.get("uid") or "").upper() == (uid or "").upper():
                BUS.publish("card_door", self.ctrl.last_card)

    def _on_home_event(self, ev):
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

    def start(self):
        self.scanner.start()
        self.idcard.start()
        if self.idcard_web:
            self.idcard_web.start()
        if self.rfid:
            self.rfid.start()
        self.home.start()
        self.audio.say("芯宿智控自助入住一体机已启动")
        log("[app] ready, camera=%s lock=%s idcard=%s rfid=%s" % (
            self.camera.node, self.lock.transport,
            "webapi" if self.idcard_web else "bridge/mock",
            "serial" if self.rfid else "hid/none"))
        threading.Thread(target=self._log_keeper, daemon=True, name="logkeeper").start()

    @staticmethod
    def _log_keeper():
        """相机 SDK 会持续刷 fps 日志，定期截断防止写满磁盘。"""
        while True:
            time.sleep(300)
            try:
                if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 20 * 1024 * 1024:
                    with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                        tail = f.readlines()[-2000:]
                    with open(LOG_FILE, "w", encoding="utf-8") as f:
                        f.writelines(tail)
                    log("[app] 日志已截断（保留最后 2000 行）")
            except Exception:
                pass

    # 扫码/读卡输入统一入口
    def _on_scan(self, code, kind, dev_name):
        step = self.ctrl.state["step"]
        self.db.audit("scan", {"code": code, "kind": kind, "device": dev_name, "step": step})
        BUS.publish("scan", {"code": code, "kind": kind, "device": dev_name, "step": step})
        if kind == "rfid":
            self.ctrl.on_card(code.upper())        # 读卡器/HID 房卡
        elif kind == "qr" and step == "pay":
            self.ctrl.on_paycode(code)             # 扫码枪只用于付款码

    # 门锁板上报的硬件事件（键盘 / NFC / 指纹 / 门磁 / 告警）
    def _on_lock_event(self, kind, value):
        self.db.audit("lock_event", {"type": kind, "value": value})
        BUS.publish("lock", {"type": kind, "value": value,
                             "room": (self.ctrl.state.get("room") or {}).get("no")})
        if kind == "CARDBIND":
            # 形如 "8805|0AD21E00"：客人在门锁板首刷，把卡号记到该房间订单上
            try:
                room, uid = (value or "").split("|", 1)
                room, uid = room.strip(), uid.strip().upper()
                n = 0
                for o in self.db.inhouse_orders():
                    if str(o["room"]) == room:
                        self.db.set_order_card(o["id"], uid)
                        n += 1
                        break
                log("[lock] 房卡绑定同步: 房间 %s <- 卡 %s (%d)" % (room, uid, n))
                BUS.publish("card_bound", {"room": room, "uid": uid})
            except Exception as e:
                log("[lock] CARDBIND 处理失败: %s (value=%r)" % (e, value))
        elif kind == "DOOR":
            log("[lock] 门磁：%s" % value)
        elif kind == "ALARM":
            log("[lock] 告警：%s" % value)
    def _on_idcard(self, name, idno, extra=None):
        """读卡器回调：先记住证件照路径，再交给状态机。"""
        if extra and extra.get("photo_path"):
            self.ctrl.id_photo_path = extra["photo_path"]
            log("[idcard] 证件照可用于比对: %s" % extra["photo_path"])
            self.face.precompute_id(extra["photo_path"], key=idno)   # 后台先算特征
        return self.ctrl.on_idcard(name, idno, extra)

    def verify_face(self, d=None):
        """证件照 vs 摄像头连拍 → 本地模型判定。

        返回 {ok, decision, score, reason, ms, frames, photo_path}
        d 里可选：idphoto（证件照路径）、livefiles（现场照路径列表），仅调试用。
        """
        import numpy as _np

        d = d or {}
        _debug = bool(CONF.get("kiosk", {}).get("face_debug", False))
        id_path = (d.get("idphoto") if _debug else None) or getattr(self.ctrl, "id_photo_path", None)
        if not id_path or not os.path.exists(id_path):
            return {"ok": False, "decision": "retry", "score": 0.0,
                    "reason": "没有读到证件照片，请把身份证重新放到读卡区", "ms": 0}

        try:
            import cv2 as _cv
        except Exception as e:
            return {"ok": False, "decision": "error", "score": 0.0,
                    "reason": "本机缺少 opencv：%s" % e, "ms": 0}

        id_bgr = _cv.imread(id_path)
        if id_bgr is None:
            return {"ok": False, "decision": "retry", "score": 0.0,
                    "reason": "证件照片读取失败，请重新刷卡", "ms": 0}
        # 读卡器给的是缩略图（常见 102x126），人脸只有 50px 上下；
        # 放大到 400px 量级再做对齐，特征会稳一些。
        ih, iw = id_bgr.shape[:2]
        if min(ih, iw) < 240:
            f = 400.0 / min(ih, iw)
            id_bgr = _cv.resize(id_bgr, (int(iw * f), int(ih * f)),
                                interpolation=_cv.INTER_CUBIC)
            log("[face] 证件照 %dx%d 已放大到 %dx%d" % (iw, ih, id_bgr.shape[1], id_bgr.shape[0]))

        # 连拍 3 帧（间隔 0.18s，让表情/姿态略有变化，便于多帧判定）
        frames = []
        live_files = d.get("livefiles") if _debug else None
        if live_files:
            for p in (live_files if isinstance(live_files, list) else [live_files]):
                img = _cv.imread(p)
                if img is not None:
                    frames.append(img)
        else:
            n = int(d.get("frames") or 3)
            for _ in range(max(1, min(n, 5))):
                data = self.camera.jpeg(640, 88)
                if data:
                    arr = _np.frombuffer(data, _np.uint8)
                    img = _cv.imdecode(arr, _cv.IMREAD_COLOR)
                    if img is not None:
                        frames.append(img)
                time.sleep(0.18)

        if not frames:
            return {"ok": False, "decision": "retry", "score": 0.0,
                    "reason": "摄像头没有画面，请检查摄像头连接", "ms": 0}

        # 现场照留档（只留一帧，便于排查；不用于训练）
        shot = None
        try:
            ts = time.strftime("%Y%m%d_%H%M%S")
            shot = os.path.join(os.environ.get("ZHIKONG_HOME", "/opt/zhikong"),
                                "data", "photos", "face_%s.jpg" % ts)
            os.makedirs(os.path.dirname(shot), exist_ok=True)
            _cv.imwrite(shot, frames[-1])
        except Exception:
            shot = None

        r = self.face.verify(id_bgr, frames, id_path=id_path,
                                 id_key=((self.ctrl.state or {}).get("idno")))
        r["photo_path"] = shot
        r["frames"] = len(frames)
        log("[face] 结论=%s 分数=%.3f 耗时=%dms 帧数=%d %s" % (
            r.get("decision"), r.get("score", 0), r.get("ms", 0),
            len(frames), r.get("reason", "")))
        return r



APP = None


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "zhikong-k1/1.0"

    # ---------- 基础 ----------
    def log_message(self, fmt, *args):
        pass

    def _send(self, code, body=b"", ctype="application/json; charset=utf-8", headers=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, obj)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        raw = self.rfile.read(n)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    def _static(self, rel, base):
        rel = urllib.parse.unquote(rel).lstrip("/")
        path = os.path.normpath(os.path.join(base, rel))
        if not path.startswith(os.path.normpath(base)) or not os.path.isfile(path):
            return self._send(404, b"not found", "text/plain; charset=utf-8")
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        with open(path, "rb") as f:
            data = f.read()
        self._send(200, data, ctype)

    # ---------- GET ----------
    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        p = u.path
        try:
            if p in ("/", "/index.html"):
                return self._static("index.html", WEB_DIR)
            if p.startswith("/static/"):
                return self._static(p[len("/static/"):], WEB_DIR)
            if p.startswith("/voice/"):
                return self._static(p[len("/voice/"):], VOICE_DIR)
            if p == "/api/net":
                ip, ssid = "", ""
                try:
                    out = subprocess.run(["hostname", "-I"], capture_output=True,
                                         text=True, timeout=2).stdout.split()
                    for x in out:
                        if ":" not in x and not x.startswith("127."):
                            ip = x
                            break
                except Exception:
                    pass
                try:
                    r = subprocess.run(["nmcli", "-t", "-f", "GENERAL.CONNECTION",
                                        "device", "show", "wlan0"],
                                       capture_output=True, text=True, timeout=2).stdout
                    if ":" in r:
                        ssid = r.strip().split(":", 1)[1]
                except Exception:
                    pass
                return self._json({"ip": ip, "ssid": ssid, "host": "shiqi.local"})
            if p == "/api/home":
                st = APP.home.status()
                g = (st.get("data") or {}).get("gas") or 0
                st["alarm"] = bool(g > 2500)
                return self._json(st)
            if p.startswith("/photos/"):
                return self._static(p[len("/photos/"):],
                                    os.path.join(os.environ.get("ZHIKONG_HOME", "/opt/zhikong"), "data", "photos"))
            if p == "/api/state":
                return self._json(APP.ctrl.snapshot())
            if p == "/api/devices":
                return self._json(APP.registry.snapshot(force=True))
            if p == "/api/health":
                return self._json({"ok": True, "ts": time.time(), "hotel": CONF["hotel"],
                                   "camera": APP.camera.info(), "lock": APP.lock.status(),
                 "home": APP.home.status(),
                                   "audio": APP.audio.info(),
                                   "idcard": (APP.idcard_web.info() if APP.idcard_web
                                              else {"mode": "bridge"}),
                                   "rfid": (APP.rfid.status() if APP.rfid
                                            else {"transport": "none"}),
                                   "lock_driver": APP.lock.transport})
            if p == "/api/workorders":
                return self._json({"items": APP.db.workorders(20)})
            if p == "/api/audit":
                return self._json({"items": APP.db.recent_audit(40)})
            if p == "/api/camera/snapshot.jpg":
                data = APP.camera.jpeg(720, 85)
                if not data:
                    return self._send(503, b"camera unavailable", "text/plain")
                return self._send(200, data, "image/jpeg")
            if p == "/api/camera/stream":
                return self._stream_mjpeg()
            if p == "/api/events":
                return self._stream_sse()
        except BrokenPipeError:
            return
        except Exception:
            log("GET %s failed: %s" % (p, traceback.format_exc()))
            return self._json({"ok": False, "error": "server error"}, 500)
        self._send(404, b"not found", "text/plain; charset=utf-8")

    def do_HEAD(self):
        self.do_GET()

    def _stream_mjpeg(self):
        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            for chunk in APP.camera.mjpeg(10):
                self.wfile.write(chunk)
        except Exception:
            pass
        self.close_connection = True

    def _stream_sse(self):
        q = BUS.subscribe()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()
        try:
            self.wfile.write(("event: hello\ndata: %s\n\n" % json.dumps({"ok": True})).encode())
            self.wfile.flush()
            last = time.time()
            while True:
                try:
                    evt = q.get(timeout=1.0)
                    self.wfile.write(sse_format(evt).encode())
                except Exception:
                    if time.time() - last > 15:
                        self.wfile.write(b": ping\n\n")
                        last = time.time()
                        continue
                self.wfile.flush()
                last = time.time()
        except Exception:
            pass
        finally:
            BUS.unsubscribe(q)
            self.close_connection = True

    # ---------- POST ----------
    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        p = u.path
        try:
            if p == "/api/session/start":
                APP.audio.flush()
                return self._json(APP.ctrl.start())
            if p == "/api/idcard/mock":
                APP.ctrl.mock_idcard()
                return self._json(APP.ctrl.snapshot())
            if p == "/api/idcard/inject":
                ok = APP.idcard.inject(self._body())
                return self._json({"ok": ok})
            if p == "/api/face":
                return self._json(self._face())
            if p.startswith("/api/room/"):
                no = p.rsplit("/", 1)[-1]
                return self._json(APP.ctrl.choose_room(no))
            if p == "/api/pay":
                return self._json(APP.ctrl.on_paycode(self._body().get("code", "MOCKPAY")))
            if p == "/api/card":
                _uid = self._body().get("uid", "MOCKCARD")
                snap = APP.ctrl.on_card(_uid)
                _lc = getattr(APP.ctrl, "last_card", None)
                if _lc and _lc.get("mode") == "checkout" and (_lc.get("uid") or "").upper() == (_uid or "").upper():
                    BUS.publish("card_door", APP.ctrl.last_card)
                return self._json(snap)
            if p == "/api/lock/resync":
                # 把当前在住订单的凭证重新下发到门锁板
                items = APP.db.inhouse_orders()
                okn = 0
                fails = []
                for o in items:
                    try:
                        ok, detail = APP.lock.issue(
                            str(o["room"]), o["guest"] or "客人",
                            o["lock_code"], o["card_uid"] or "-", 24 * 60)
                    except Exception as e:
                        ok, detail = False, str(e)
                    if ok:
                        okn += 1
                    else:
                        fails.append({"room": o["room"], "detail": str(detail)[:60]})
                return self._json({"ok": True, "total": len(items),
                                   "issued": okn, "failed": fails})
            if p == "/api/checkout/guide":
                return self._json(APP.ctrl.checkout_guide())

            if p == "/api/lock/code":
                # 门锁板本地校验开门码（模拟门锁键盘输入）
                pin = str(self._body().get("pin", "")).strip()
                ok, detail = APP.lock.validate_code(pin)
                if ok:
                    APP.lock.open_door((APP.ctrl.state.get("room") or {}).get("no") or "-", "pin")
                BUS.publish("lock_verify", {"ok": ok, "detail": str(detail)[:40]})
                return self._json({"ok": ok, "detail": detail})
            if p == "/api/issue":
                return self._json(APP.ctrl.issue())
            if p == "/api/cancel":
                APP.audio.flush()
                return self._json(APP.ctrl.cancel())
            if p == "/api/reset":
                # 完成并返回：只回待机，保留门锁凭证
                APP.audio.flush()
                return self._json(APP.ctrl.reset())
            if p == "/api/home":
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
            if p == "/api/checkout":
                # 退房：room=房间（前台用）；pin=开门码（客人自助用）
                APP.audio.flush()
                body = self._body()
                pin = str(body.get("pin", "") or "").strip()
                if pin:
                    return self._json(APP.ctrl.checkout_by_code(pin))
                room = str(body.get("room", "") or "").strip() or None
                return self._json(APP.ctrl.checkout(room))
            if p == "/api/back":
                APP.audio.flush()
                return self._json(APP.ctrl.back())
            if p == "/api/voice":
                d = self._body()
                return self._json(APP.ctrl.voice(d.get("text", ""), d.get("room")))
            if p == "/api/lock/open":
                d = self._body()
                ok, msg = APP.lock.open_door(d.get("room"), d.get("method", "kiosk"))
                return self._json({"ok": ok, "msg": msg})
            if p == "/api/kiosk/exit":
                # 长按 logo 退出：关掉浏览器窗口，回到桌面（后端继续跑）
                log("[app] kiosk exit requested")
                subprocess.Popen(["pkill", "-f", "chromium.*127.0.0.1:8080"])
                return self._json({"ok": True, "msg": "已退出到桌面"})
            if p == "/api/workorders/next":
                w = APP.db.next_workorder()
                if w:
                    APP.db.set_workorder_status(w["id"], "accepted")
                return self._json({"item": w})
            if p == "/api/sim/scan":
                d = self._body()
                APP._on_scan(d.get("code", "SIM123456"), d.get("kind", "qr"), "simulator")
                return self._json(APP.ctrl.snapshot())
            if p == "/api/debug/click":
                d = self._body()
                log("[ui] %s %s,%s type=%s target=%s" % (d.get("ev"), d.get("x"), d.get("y"),
                                                         d.get("type"), d.get("target")))
                return self._json({"ok": True})
        except Exception:
            log("POST %s failed: %s" % (p, traceback.format_exc()))
            return self._json({"ok": False, "error": "server error"}, 500)
        self._send(404, b"not found", "text/plain; charset=utf-8")

    def _face(self):
        d = self._body()
        if APP.ctrl.state["step"] != "face":
            return APP.ctrl.snapshot()
        # 测试模式：不采集画面，直接放行（客户要的"走个样子"）
        if CONF.get("kiosk", {}).get("face_sim", True) and not d.get("real"):
            APP.ctrl.on_face(None, 0.96)
            return APP.ctrl.snapshot()
        if d.get("skip"):
            # 测试模式：人脸页点「跳过人脸」，直接放行（审计里留痕）
            log("[face] 测试跳过（未做人脸比对）")
            APP.ctrl.on_face(None, 0.99)
            snap = APP.ctrl.snapshot()
            snap["face"] = {"ok": True, "decision": "skip", "score": 0.99,
                            "reason": "测试模式：已跳过人脸比对", "ms": 0}
            return snap

        if CONF.get("kiosk", {}).get("face_sim", False) and not d.get("real"):
            # 显式要求模拟（演示/无模型时的兜底）
            APP.ctrl.on_face(None, 0.96)
            return APP.ctrl.snapshot()

        res = APP.verify_face(d)
        path = res.get("photo_path")
        APP.ctrl.on_face(
            ("/photos/" + os.path.basename(path)) if path else None,
            res.get("score", 0.0),
            passed=bool(res.get("ok")),
            reason=res.get("reason", ""),
        )
        snap = APP.ctrl.snapshot()
        snap["face"] = {k: v for k, v in res.items() if k != "photo_path"}
        return snap

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Content-Length", "0")
        self.end_headers()


def main():
    global APP
    port = int(os.environ.get("ZHIKONG_PORT", CONF["kiosk"].get("port", 8080)))
    APP = App()
    APP.start()
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    srv.daemon_threads = True
    log("[app] listening on 0.0.0.0:%d" % port)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
