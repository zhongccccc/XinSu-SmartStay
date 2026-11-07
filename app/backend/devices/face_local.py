"""本机人脸比对：封装 /opt/zhikong/face 下的 face_verify_k1。

一体机侧只依赖这一个类：
    v = LocalFaceVerifier()
    if v.available():
        r = v.verify(id_bgr, [frame1, frame2, frame3])
        # r = {"ok": True, "decision": "pass", "score": 0.61, "reason": "", "ms": 1450}
"""

from __future__ import annotations

import os
import sys
import threading
import time

import numpy as np


def scores_ok(errs):
    return False


class LocalFaceVerifier:
    def __init__(self, home="/opt/zhikong/face", config="config.yaml", log=print):
        self.home = home
        self.config_path = os.path.join(home, config)
        self.log = log
        self._verifier = None
        self._err = ""
        self._lk = threading.Lock()
        self._loaded = False
        self._id_cache = {}          # path -> (embedding, 时间戳)
        self._id_lock = threading.Lock()

    # ---------- 就绪判断 ----------
    def available(self):
        return os.path.exists(self.config_path) and os.path.isdir(os.path.join(self.home, "facekit"))

    def _load(self):
        if self._loaded:
            return self._verifier
        with self._lk:
            if self._loaded:
                return self._verifier
            try:
                if self.home not in sys.path:
                    sys.path.insert(0, self.home)
                from facekit.config import Config
                from facekit.pipeline import FaceVerifier

                t0 = time.time()
                cfg = Config.load(self.config_path)
                self._verifier = FaceVerifier(cfg)
                self._loaded = True
                self.log("[face] 模型加载完成 %.1fs" % (time.time() - t0))
            except Exception as e:
                self._err = "%s: %s" % (type(e).__name__, e)
                self.log("[face] 加载失败 %s" % self._err)
                self._loaded = True
                self._verifier = None
        return self._verifier

    # ---------- 比对 ----------

    def embed_id(self, id_path, key=None):
        """算证件照特征（带缓存）。返回 numpy 数组或 None。"""
        if not id_path:
            return None
        cache_key = key or id_path
        with self._id_lock:
            hit = self._id_cache.get(cache_key)
            if hit is not None:
                return hit

        v = self._load()
        if v is None:
            return None
        try:
            import cv2 as _cv
            img = _cv.imread(id_path)
            if img is None:
                return None
            h, w = img.shape[:2]
            if min(h, w) < 240:
                f = 400.0 / min(h, w)
                img = _cv.resize(img, (int(w * f), int(h * f)), interpolation=_cv.INTER_CUBIC)
            t0 = time.time()
            ext = v.embed_id_photo(img)
            with self._id_lock:
                self._id_cache = {cache_key: ext.embedding}   # 只留最近一张
            self.log("[face] 证件照特征已算好 %.0fms" % ((time.time() - t0) * 1000))
            return ext.embedding
        except Exception as e:
            self.log("[face] 证件照特征计算失败: %s: %s" % (type(e).__name__, e))
            return None

    def precompute_id(self, id_path, key=None):
        """后台预热（刷卡后调用）。"""
        import threading as _t
        _t.Thread(target=self.embed_id, args=(id_path,), kwargs={'key': key}, daemon=True).start()

    def verify(self, id_bgr, live_frames, id_path=None, id_key=None):
        v = self._load()
        if v is None:
            return {"ok": False, "decision": "error", "score": 0.0,
                    "reason": "比对模块不可用：" + self._err, "ms": 0}

        t0 = time.time()
        try:
            r = v.verify(id_bgr, live_frames)
        except Exception as e:
            return {"ok": False, "decision": "error", "score": 0.0,
                    "reason": "比对异常：%s: %s" % (type(e).__name__, e),
                    "ms": int((time.time() - t0) * 1000)}

        ms = int((time.time() - t0) * 1000)
        decision = getattr(r, "decision", None) or "error"
        score = float(getattr(r, "score", 0.0) or 0.0)
        frames = getattr(r, "frames", []) or []
        reason = ""
        for f in frames:
            why = getattr(f, "reason", "") or (f.get("reason") if isinstance(f, dict) else "")
            if why:
                reason = why
                break
        if not reason:
            reason = getattr(r, "reason", "") or ""
        # 区分「没检测到人脸」与「质量不合格」，给客人更准确的提示
        errs = []
        for f in frames:
            e = getattr(f, "error", "") or ""
            if e:
                errs.append(e)
        if errs and all("未检测到人脸" in e for e in errs):
            reason = "画面里没有检测到人脸，请正对摄像头、让脸部占满取景框"
        elif errs and not scores_ok(errs):
            reason = "画面质量不达标：" + errs[0]
        return {
            "ok": decision == "pass",
            "decision": decision,            # pass / retry / review / error
            "score": round(score, 4),
            "reason": reason,
            "ms": ms,
            "frames": len(frames),
        }

    def warmup(self):
        """启动时预热，避免第一次核验卡住。"""
        if not self.available():
            return False
        v = self._load()
        if v is None:
            return False
        try:
            blank = np.zeros((112, 112, 3), np.uint8)
            v.verify(blank, [blank])
            return True
        except Exception:
            return False
