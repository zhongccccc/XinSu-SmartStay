#!/bin/bash
set -e
D=/home/openharmony/txsmartropenharmony/applications/sample/wifi-iot/app/zhikong_home

# 1) 删掉 lcd.c 里多出来的一个 }
python3 - "$D/lcd.c" <<'PY'
import sys
p = sys.argv[1]
lines = open(p, encoding='utf-8', errors='replace').read().splitlines()
# 找到 lcd_show_picture 结束后的孤立 '}'
out = []
i = 0
while i < len(lines):
    if (lines[i].strip() == '}' and i + 1 < len(lines)
            and lines[i + 1].strip() == '}'
            and i > 0 and 'lcd_write_buf(pic' in lines[i - 2]):
        # 保留第一个，跳过第二个
        out.append(lines[i])
        i += 2
        continue
    out.append(lines[i])
    i += 1
open(p, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print("lcd.c 已清理")
PY

# 2) zh_home.c 里 LCD_ORANGE -> LCD_YELLOW
sed -i 's/LCD_ORANGE/LCD_YELLOW/g' "$D/zh_home.c"
grep -c 'LCD_YELLOW' "$D/zh_home.c"

# 3) 检查 lcd.c 尾部是否还有孤立 }
python3 - "$D/lcd.c" <<'PY'
import sys
s = open(sys.argv[1], encoding='utf-8', errors='replace').read()
print("大括号平衡:", s.count('{') - s.count('}'))
PY
