#!/bin/bash
echo "=== trace 前 20 行 ==="
head -20 /tmp/tr5.txt
echo
echo "=== trace 后 25 行 ==="
tail -25 /tmp/tr5.txt
echo
echo "=== 含 ENOENT / EACCES 的行（前 10）==="
grep -E "ENOENT|EACCES|EPERM" /tmp/tr5.txt | head -10
echo
echo "=== 出现过的绝对路径（去重）==="
grep -oE '"/[^"]{3,80}"' /tmp/tr5.txt | sort | uniq -c | sort -rn | head -20
