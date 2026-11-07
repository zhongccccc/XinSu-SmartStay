#!/bin/bash
cd /tmp
timeout 40 chromium-browser --headless --disable-gpu --no-sandbox \
  --enable-logging=stderr --v=0 --virtual-time-budget=4000 \
  --user-data-dir=/tmp/hl-chk --dump-dom http://127.0.0.1:8080/ \
  > /tmp/dom.html 2> /tmp/js.log
echo "=== JS 错误 ==="
grep -iE 'uncaught|SyntaxError|ReferenceError|TypeError|CONSOLE' /tmp/js.log | head -12
echo
echo "=== DOM 里 idle 标题是否存在 ==="
grep -c '欢迎光临' /tmp/dom.html
