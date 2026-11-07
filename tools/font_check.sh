#!/bin/bash
cd /home/openharmony/txsmartropenharmony/applications/sample/wifi-iot/app/zhikong_home
echo "=== lcd_font.h ==="
ls -l lcd_font.h 2>/dev/null | awk '{print $5, $9}'
echo "=== 中文字模结构（前几行）==="
grep -n 'chinese\|Chinese\|ChineseFont\|typedef' lcd_font.h | head -10
echo
echo "=== 字库里出现的中文字符（去重）==="
python3 - <<'PY'
import re
s = open('lcd_font.h', encoding='utf-8', errors='replace').read()
chars = sorted(set(re.findall(r'[\u4e00-\u9fff]', s)))
print("共 %d 个汉字:" % len(chars))
print("".join(chars))
PY
