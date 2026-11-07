# -*- coding: utf-8 -*-
"""极简事件总线 + SSE 推送。"""
import json
import queue
import threading
import time


class Bus:
    def __init__(self):
        self._subs = set()
        self._lock = threading.Lock()
        self._seq = 0

    def subscribe(self):
        q = queue.Queue(maxsize=64)
        with self._lock:
            self._subs.add(q)
        return q

    def unsubscribe(self, q):
        with self._lock:
            self._subs.discard(q)

    def publish(self, topic, data=None):
        with self._lock:
            self._seq += 1
            evt = {"seq": self._seq, "topic": topic, "ts": time.time(), "data": data or {}}
            dead = []
            for q in self._subs:
                try:
                    q.put_nowait(evt)
                except queue.Full:
                    dead.append(q)
            for q in dead:
                self._subs.discard(q)
        return evt


BUS = Bus()


def sse_format(evt):
    return "event: %s\ndata: %s\n\n" % (evt["topic"], json.dumps(evt, ensure_ascii=False))
