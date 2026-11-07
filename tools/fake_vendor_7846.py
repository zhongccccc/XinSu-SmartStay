#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按厂商 WebAPI 的真实返回结构造的假服务，验证 K1 侧解析。"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

BODY = {
    "errorMsg": "OK",
    "resultFlag": "0",
    "status": "0",
    "verderId": "1000",
    "resultContent": {
        "address": "广东省深圳市宝安区新安街道66号",
        "birthday": "20051007",
        "effectDate": "20210601",
        "expireDate": "20410601",
        "gender": "1",
        "idNum": "440306200510071234",
        "issueOrg": "深圳市公安局宝安分局",
        "name": "张三",
        "nation": "01",
        "photo": "",
    },
}


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/readCard"):
            data = json.dumps(BODY, ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 7846), H).serve_forever()
