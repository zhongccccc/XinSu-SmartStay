# -*- coding: utf-8 -*-
"""音频：ALSA 播报队列 / 离线 TTS / 麦克风录音。"""
import glob
import hashlib
import os
import queue
import re
import subprocess
import threading

from ..config import VOICE_DIR

def _detect_card():
    """优先用 USB 声卡（外接音箱），没有就退回板载 ES8326。

    可以用环境变量 ZHIKONG_ALSA 强制指定，例如 plughw:1,0。
    """
    env = os.environ.get("ZHIKONG_ALSA")
    if env:
        return env
    try:
        with open("/proc/asound/cards", "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                m = re.match(r"\s*(\d+)\s+\[", line)
                if not m:
                    continue
                if "usb" in line.lower():
                    return "plughw:%s,0" % m.group(1)
    except Exception:
        pass
    return "plughw:1,0"


CARD = _detect_card()


def _which(b):
    for p in os.environ.get("PATH", "").split(":"):
        f = os.path.join(p, b)
        if os.path.isfile(f) and os.access(f, os.X_OK):
            return f
    return None


class Audio:
    def __init__(self, log=print):
        self.log = log
        self.aplay = _which("aplay")
        self.pwplay = _which("pw-play") or _which("paplay")
        self.setpriv = _which("setpriv")
        # PipeWire 属于桌面登录用户（默认 1000）。后端是 root，
        # 必须切到这个用户才能连上 /run/user/1000/pipewire-0。
        self.run_uid = os.environ.get("ZHIKONG_AUDIO_UID", "1000")
        self.arecord = _which("arecord")
        self.espeak = _which("espeak-ng") or _which("espeak")
        self.ffmpeg = _which("ffmpeg")
        self._q = queue.Queue()
        self._stop = False
        self.playing = None
        threading.Thread(target=self._worker, daemon=True, name="audio").start()

    # ---------- TTS ----------
    def wav_path(self, text):
        h = hashlib.md5(text.encode("utf-8")).hexdigest()[:12]
        return os.path.join(VOICE_DIR, "%s.wav" % h)

    def synth(self, text, force=False):
        """离线合成；已有预置音频则直接复用。统一重采样到 48kHz 单声道，
        因为 ES8326 不接受 22.05kHz 直出。"""
        path = self.wav_path(text)
        if os.path.exists(path) and os.path.getsize(path) > 1000 and not force:
            return path
        if not self.espeak:
            return None
        raw = path + ".raw"
        try:
            subprocess.run([self.espeak, "-v", "cmn", "-s", "150", "-p", "55",
                            "-w", raw, text], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
        except Exception as e:
            self.log("[audio] tts failed: %s" % e)
            return None
        try:
            if self.ffmpeg:
                subprocess.run([self.ffmpeg, "-loglevel", "error", "-y", "-i", raw,
                                "-ar", "48000", "-ac", "1", path], check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
                os.remove(raw)
            else:
                os.replace(raw, path)
            return path if os.path.exists(path) else None
        except Exception as e:
            self.log("[audio] resample failed: %s" % e)
            return raw if os.path.exists(raw) else None

    def say(self, text, priority=False):
        if not text:
            return
        self._q.put(("say", text))
        if priority:
            self.flush()

    def play_file(self, path):
        if path and os.path.exists(path):
            self._q.put(("play", path))

    def flush(self):
        while True:
            try:
                self._q.get_nowait()
            except queue.Empty:
                break
        cur = self.playing
        if cur and cur.poll() is None:
            try:
                cur.terminate()
            except Exception:
                pass

    def _worker(self):
        while not self._stop:
            kind, val = self._q.get()
            try:
                path = val if kind == "play" else self.synth(val)
                if not path or not self.aplay:
                    continue
                if self.pwplay:
                    cmd = [self.pwplay, path]
                    if os.geteuid() == 0 and self.setpriv:
                        cmd = [self.setpriv, "--reuid=" + self.run_uid,
                               "--regid=" + self.run_uid, "--init-groups"] + cmd
                elif self.aplay:
                    cmd = [self.aplay, "-q", "-D", CARD, path]
                else:
                    continue
                env = dict(os.environ)
                env.setdefault("XDG_RUNTIME_DIR", "/run/user/" + self.run_uid)
                self.playing = subprocess.Popen(
                    cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
                self.playing.wait(timeout=30)
            except Exception as e:
                self.log("[audio] play failed: %s" % e)
            finally:
                self.playing = None

    # ---------- 录音 ----------
    def record(self, seconds=4, path=None):
        if not self.arecord:
            return None
        path = path or os.path.join(VOICE_DIR, "mic_%d.wav" % int(os.times().elapsed))
        try:
            subprocess.run([self.arecord, "-q", "-D", CARD, "-f", "S16_LE", "-r", "16000",
                            "-c", "1", "-d", str(seconds), path],
                           timeout=seconds + 10, check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return path
        except Exception as e:
            self.log("[audio] record failed: %s" % e)
            return None

    def info(self):
        cards = []
        try:
            with open("/proc/asound/cards", "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("---"):
                        cards.append(line)
        except Exception:
            pass
        return {"ok": bool(cards), "cards": cards, "tts": bool(self.espeak),
                "alsa": CARD, "player": ("pw-play" if self.pwplay else "aplay")}
