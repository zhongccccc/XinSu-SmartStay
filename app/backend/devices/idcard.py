# -*- coding: utf-8 -*-
"""二代身份证读卡器接入点。

读卡器厂商 SDK（多为 Windows DLL / 私有 HID 协议）不在这里硬解，
本模块提供统一入口：任何桥接进程只要把读到的证件信息写到
  /run/zhikong/idcard.json
或 POST /api/idcard/inject，业务层即收到一次"刷卡"事件。
这样换任何品牌的读卡器，只需替换桥接脚本，一体机业务零改动。
"""
import json
import os
import time

INJECT_FILE = os.environ.get("ZHIKONG_IDCARD_FILE", "/run/zhikong/idcard.json")
MOCK_CARDS = [
    {"name": "陈思远", "idno": "440305199203182418", "sex": "男", "nation": "汉",
     "birth": "1992-03-18", "addr": "深圳市南山区科技园南路 18 号"},
    {"name": "李梦琪", "idno": "440306199508120627", "sex": "女", "nation": "汉",
     "birth": "1995-08-12", "addr": "深圳市宝安区新安街道 66 号"},
    {"name": "王浩然", "idno": "440304198811055513", "sex": "男", "nation": "汉",
     "birth": "1988-11-05", "addr": "深圳市福田区深南大道 1000 号"},
]


class IdCardReader:
    def __init__(self, on_card, log=print):
        self.on_card = on_card
        self.log = log
        self.last_ts = 0
        self._seen = None
        self._i = 0

    def start(self):
        import threading
        threading.Thread(target=self._watch, daemon=True, name="idcard").start()

    def _watch(self):
        while True:
            try:
                if os.path.exists(INJECT_FILE):
                    st = os.stat(INJECT_FILE)
                    if self._seen != (st.st_mtime, st.st_size) and st.st_size > 4:
                        self._seen = (st.st_mtime, st.st_size)
                        with open(INJECT_FILE, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        self.inject(data)
            except Exception as e:
                self.log("[idcard] watch: %s" % e)
            time.sleep(0.5)

    def inject(self, data):
        name = data.get("name") or data.get("姓名") or ""
        idno = data.get("idno") or data.get("id") or data.get("身份证号") or ""
        if not name or not idno:
            self.log("[idcard] rejected payload: %r" % (data,))
            return False
        self.last_ts = time.time()
        self.log("[idcard] %s %s" % (name, idno[:6] + "********" + idno[-4:]))
        try:
            self.on_card(name, idno, data)
        except Exception as e:
            self.log("[idcard] callback error: %s" % e)
        return True

    def mock(self):
        card = MOCK_CARDS[self._i % len(MOCK_CARDS)]
        self._i += 1
        return self.inject(dict(card))

    def info(self):
        return {"inject_file": INJECT_FILE, "last_ts": self.last_ts}
