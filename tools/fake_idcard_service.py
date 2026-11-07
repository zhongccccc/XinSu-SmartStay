#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""假的厂商读卡服务：验证 K1 侧 WebAPI 客户端链路。"""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

CARD = {
    "code": "0",
    "retcode": "0x90 0x1",
    "retmsg": "读卡成功",
    "name": "陈思远",
    "sex": "男",
    "nation": "汉",
    "born": "19920318",
    "address": "广东省深圳市南山区科技园南路18号",
    "cardno": "440305199203182418",
    "police": "深圳市公安局南山分局",
    "userlifeb": "20180301",
    "userlifee": "20380301",
    "photobase64": "",
}


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/readCard"):
            body = json.dumps(CARD, ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 7846), H).serve_forever()
