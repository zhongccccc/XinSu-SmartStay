#!/bin/bash
echo "=== /static/app.js 头部 ==="
curl -s -D- http://127.0.0.1:8080/static/app.js -o /tmp/a.js | head -8
echo -n "字节: "; wc -c < /tmp/a.js
echo -n "含 bindCheckout: "; grep -c bindCheckout /tmp/a.js || true
echo
echo "=== index.html 里的引用 ==="
curl -s http://127.0.0.1:8080/ | grep -o 'static/[a-z.]*' || true
