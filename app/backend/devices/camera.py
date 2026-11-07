# -*- coding: utf-8 -*-
"""摄像头：优先用 SpaceMiT 的 MIPI 取流管线（IMX219），回退到普通 V4L2 节点。

K1 的 MIPI 摄像头走 spacemitsrc（GStreamer），普通 v4l2src / VideoCapture(节点)
会因为 NV12 非连续平面缓冲失败，所以这里以管线为主。

持续取流放在后台线程里，只保留最新一帧（并缩到 640 宽），
这样 MJPEG 预览、抓拍、人脸采集都读同一份缓存，不会互相抢流。
"""
import glob
import os
import threading
import time

try:
    import cv2
except Exception:  # pragma: no cover
    cv2 = None


def _node_name(path):
    idx = path.rsplit("video", 1)[-1]
    try:
        with open("/sys/class/video4linux/video%s/name" % idx, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""


def candidate_nodes(exclude_re=""):
    import re
    pat = re.compile(exclude_re) if exclude_re else None
    out = []
    for p in sorted(glob.glob("/dev/video*")):
        n = _node_name(p)
        if not n or "mvx" in n or "vivi" in n or "dec" in n:
            continue
        if pat and pat.search(n):
            continue
        out.append((p, n))
    return out


class Camera:
    def __init__(self, exclude_re="", log=print, pipeline="", cfg_path=""):
        self.log = log
        self.exclude_re = exclude_re
        self.pipeline = pipeline.replace("{cfg}", cfg_path) if pipeline else ""
        self.cfg_path = cfg_path
        self.node = None
        self.name = None
        self._cap = None
        self._lk = threading.Lock()
        self.last_frame = None
        self.last_ts = 0
        self._thread = None
        self._stop = False
        self.fps = 0
        self._count = 0

    # ---------- 探测 ----------
    def probe(self):
        if cv2 is None:
            return False
        if self.pipeline and os.path.exists(self.cfg_path):
            if self._open_pipeline():
                return True
        return self._probe_v4l2()

    def _open_pipeline(self):
        try:
            cap = cv2.VideoCapture(self.pipeline, cv2.CAP_GSTREAMER)
        except Exception as e:
            self.log("[camera] pipeline error: %s" % e)
            return False
        if not cap.isOpened():
            cap.release()
            self.log("[camera] spacemitsrc 管线打不开")
            return False
        with self._lk:
            self._cap = cap
            self.node = "gstreamer:spacemitsrc"
            self.name = "IMX219 (MIPI CSI)"
        self._start_reader()
        t0 = time.time()
        while time.time() - t0 < 8:
            if self.last_frame is not None:
                self.log("[camera] 管线就绪 %dx%d" % (self.last_frame.shape[1],
                                                     self.last_frame.shape[0]))
                return True
            time.sleep(0.1)
        self.log("[camera] 管线打开但 8 秒无帧")
        return False

    def _probe_v4l2(self):
        for path, name in candidate_nodes(self.exclude_re):
            cap = cv2.VideoCapture(path, cv2.CAP_V4L2)
            if not cap.isOpened():
                cap.release()
                continue
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 15)
            ok, frame = cap.read()
            if ok and frame is not None:
                with self._lk:
                    self._cap, self.node, self.name = cap, path, name
                    self.last_frame, self.last_ts = frame, time.time()
                self.log("[camera] v4l2 %s (%s)" % (path, name))
                return True
            cap.release()
        return False

    # ---------- 取流线程 ----------
    def _start_reader(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop = False
        self._thread = threading.Thread(target=self._reader, daemon=True, name="camera")
        self._thread.start()

    def _reader(self):
        fail = 0
        while not self._stop:
            cap = self._cap
            if cap is None:
                # 没有可用管线：每 10 秒重试一次探测（开机时 sensor 可能还没就绪）
                now = time.time()
                if now - getattr(self, "_last_probe", 0) > 10:
                    self._last_probe = now
                    self.log("[camera] 重新探测摄像头")
                    self.probe()
                time.sleep(0.5)
                continue
            try:
                ok, frame = cap.read()
            except Exception:
                ok, frame = False, None
            if not ok or frame is None:
                fail += 1
                if fail == 30:
                    self.log("[camera] 连续取帧失败，重开管线")
                    self._reopen()
                    fail = 0
                time.sleep(0.05)
                continue
            fail = 0
            h, w = frame.shape[:2]
            if w > 640:
                frame = cv2.resize(frame, (640, int(h * 640 / w)), interpolation=cv2.INTER_AREA)
            self.last_frame = frame
            now = time.time()
            self._count += 1
            if now - getattr(self, "_fps_ts", 0) > 1.0:
                dt = now - getattr(self, "_fps_ts", now - 1)
                self.fps = round(self._count / max(0.001, dt), 1)
                self._count = 0
                self._fps_ts = now
            self.last_ts = now

    def _reopen(self):
        with self._lk:
            try:
                if self._cap:
                    self._cap.release()
            except Exception:
                pass
            self._cap = None
        time.sleep(0.5)
        if self.pipeline:
            cap = cv2.VideoCapture(self.pipeline, cv2.CAP_GSTREAMER)
            if cap.isOpened():
                with self._lk:
                    self._cap = cap
                self.log("[camera] 管线已重开")
                return
        if self.node and str(self.node).startswith("/dev/"):
            cap = cv2.VideoCapture(self.node, cv2.CAP_V4L2)
            if cap.isOpened():
                with self._lk:
                    self._cap = cap

    # ---------- 对外 ----------
    def frame_age(self):
        """最后一帧距今多少秒；没有帧返回一个很大的数。"""
        ts = getattr(self, "last_ts", 0)
        if not ts or self.last_frame is None:
            return 999.0
        return max(0.0, time.time() - ts)

    def wait_fresh(self, max_age=2.0, timeout=3.0):
        """等一帧新鲜的；超时返回 False。"""
        end = time.time() + timeout
        while time.time() < end:
            if self.frame_age() <= max_age:
                return True
            time.sleep(0.15)
        return False

    def read(self):
        return self.last_frame

    def jpeg(self, width=640, quality=80):
        frame = self.last_frame
        if frame is None or cv2 is None:
            return None
        h, w = frame.shape[:2]
        if w > width:
            frame = cv2.resize(frame, (width, int(h * width / w)), interpolation=cv2.INTER_AREA)
        ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        return buf.tobytes() if ok else None

    def snapshot(self, path):
        # 帧过期说明管线卡住了：先重开，再等最多 3 秒
        if self.frame_age() > 2.0:
            self.log("[camera] 画面已过期 %.1fs，重开管线" % self.frame_age())
            try:
                self._reopen()
            except Exception as e:
                self.log("[camera] 重开失败: %s" % e)
            if not self.wait_fresh(1.0, 3.0):
                self.log("[camera] 重开后仍无画面，返回失败")
                return None
        data = self.jpeg(960, 88)
        if data:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(data)
            return path
        return None

    def mjpeg(self, fps=10):
        interval = 1.0 / max(1, fps)
        while True:
            data = self.jpeg(560, 65)
            if data:
                yield (b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: %d\r\n\r\n" % len(data)
                       + data + b"\r\n")
            time.sleep(interval)

    def info(self):
        return {"node": self.node, "name": self.name, "ok": self.last_frame is not None,
                "fps": self.fps,
                "age": round(time.time() - self.last_ts, 1) if self.last_ts else None}
