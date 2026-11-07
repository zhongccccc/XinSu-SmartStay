# -*- coding: utf-8 -*-
"""二代身份证读卡器 —— 通过厂商「身份证阅读服务」的 WebAPI 接入。

厂商（数据通信科学技术研究所 / bland / ZDG）的 Linux 与 Windows 服务都会在
本机 7846 端口暴露同一个接口：

    GET http://<host>:7846/api/readCard?utf8=1

返回 JSON（字段映射见厂商 http_service.cfg）：
    code / retmsg / retcode / name / sex / nation / born / address /
    cardno / userlifeb / userlifee / police / photobase64

这样服务跑在哪台机器上都可以：
  * 今天：Windows 笔记本插读卡器，K1 调它的 7846；
  * 以后：厂商给出 riscv64 版 id_reader，直接跑在 K1 本机 127.0.0.1:7846。
业务层完全不用改。
"""
import json
import threading
import time
import urllib.error
import urllib.request

# 民族代码（GB/T 3304）常见值，齐全表可后补
NATION_CODE = {
    "01": "汉", "02": "蒙古", "03": "回", "04": "藏", "05": "维吾尔", "06": "苗",
    "07": "彝", "08": "壮", "09": "布依", "10": "朝鲜", "11": "满", "12": "侗",
    "13": "瑶", "14": "白", "15": "土家", "16": "哈尼", "17": "哈萨克", "18": "傣",
    "19": "黎", "20": "傈僳", "21": "佤", "22": "畲", "23": "高山", "24": "拉祜",
    "25": "水", "26": "东乡", "27": "纳西", "28": "景颇", "29": "柯尔克孜",
    "30": "土", "31": "达斡尔", "32": "仫佬", "33": "羌", "34": "布朗", "35": "撒拉",
    "36": "毛南", "37": "仡佬", "38": "锡伯", "39": "阿昌", "40": "普米",
}


class IdCardWebApi:
    def __init__(self, on_card, base="http://127.0.0.1:7846", interval=1.5,
                 timeout=2.0, log=print):
        self.on_card = on_card
        self.base = base.rstrip("/")
        self.interval = interval
        self.timeout = timeout
        self.log = log
        self._last = None
        self._last_ts = 0.0
        self._stop = False
        self.last_ok = 0
        self.online = False

    def _get(self):
        url = self.base + "/api/readCard?utf8=1"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            raw = r.read().decode("utf-8", "ignore")
        return json.loads(raw)

    def _parse(self, d):
        """兼容不同版本服务的字段名。"""
        # 厂商新版 WebAPI 把证件字段放在 resultContent 里
        rc = d.get("resultContent") if isinstance(d.get("resultContent"), dict) else d

        def pick(*keys):
            for k in keys:
                v = rc.get(k)
                if v not in (None, ""):
                    return v
            return None

        idno = pick("idNum", "cardno", "number", "idno", "id", "身份证号")
        name = pick("name", "姓名")
        if not idno or not name:
            return None
        sex_raw = pick("gender", "sex", "性别")
        sex = {"1": "男", "2": "女"}.get(str(sex_raw), sex_raw)
        nation_raw = pick("nation", "race", "民族")
        nation = NATION_CODE.get(str(nation_raw).zfill(2), nation_raw)
        return {
            "name": name,
            "idno": str(idno),
            "sex": sex,
            "nation": nation,
            "birth": pick("birthday", "born", "出生"),
            "addr": pick("address", "addr", "住址"),
            "police": pick("issueOrg", "police", "issuer", "签发机关"),
            "valid_from": pick("effectDate", "userlifeb", "valid"),
            "valid_to": pick("expireDate", "userlifee", "expire"),
            "source": "webapi",
            # 只留业务要用的字段；照片 base64 不落库、不进审计
            "raw": {k: v for k, v in rc.items() if k not in ("photo", "photobase64")},
            "photo_b64": pick("photo", "photobase64"),
        }

    def _save_photo(self, b64):
        """把证件照 base64 存成 jpg，返回路径；失败返回 None。"""
        if not b64:
            return None
        import base64, os, time as _t
        if isinstance(b64, str) and b64.startswith('data:'):
            b64 = b64.split(',', 1)[-1]
        raw = base64.b64decode(b64) if isinstance(b64, str) else b64
        d = os.path.join(os.environ.get('ZHIKONG_HOME', '/opt/zhikong'), 'data', 'idphotos')
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, 'id_%s.jpg' % _t.strftime('%Y%m%d_%H%M%S'))
        with open(path, 'wb') as f:
            f.write(raw)
        self.log('[idcard] 证件照已保存 %s (%d KB)' % (path, len(raw)//1024))
        return path

    def poll_once(self):
        try:
            d = self._get()
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            if self.online:
                self.log("[idcard] service offline: %s" % e)
            self.online = False
            return None
        except Exception as e:
            self.log("[idcard] bad response: %s" % e)
            return None

        self.online = True
        self.last_ok = time.time()
        card = self._parse(d)
        if not card:
            return None
        # 时间窗去重：同一张卡 5 秒内不重复上报，之后允许再次触发
        # （一次入住读完卡后，下一位客人用同一张卡也要能用）
        now = time.time()
        if card["idno"] == self._last and now - self._last_ts < 5.0:
            return None
        self._last, self._last_ts = card["idno"], now
        # 日志脱敏：姓名只留姓，证件号只留前 3 后 2
        name_masked = (card["name"][:1] + "**") if card.get("name") else "**"
        idm = card["idno"]
        self.log("[idcard] %s %s" % (name_masked, idm[:3] + "**********" + idm[-2:]))
        # 证件照落盘：人脸比对要用
        try:
            card["photo_path"] = self._save_photo(card.pop("photo_b64", None))
        except Exception as e:
            card["photo_path"] = None
            self.log("[idcard] 照片保存失败: %s" % e)
        try:
            self.on_card(card["name"], card["idno"], card)
        except Exception as e:
            self.log("[idcard] callback error: %s" % e)
        return card

    def start(self):
        threading.Thread(target=self._loop, daemon=True, name="idcard-web").start()

    def _loop(self):
        while not self._stop:
            self.poll_once()
            time.sleep(self.interval)

    def info(self):
        return {"mode": "webapi", "url": self.base, "online": self.online,
                "last_ok": self.last_ok}


if __name__ == "__main__":
    import sys
    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:7846"
    api = IdCardWebApi(lambda n, i, c: print("CARD:", n, i), base=base)
    card = api.poll_once()
    if not card:
        print("no card / service offline")
    else:
        print(json.dumps({k: v for k, v in card.items() if k not in ("photo_b64", "raw")},
                         ensure_ascii=False, indent=2))
