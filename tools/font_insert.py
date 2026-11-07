import io
import re

H = "lcd_font.h"
s = open(H, encoding="utf-8", errors="replace").read()

add16 = open("font16_add.txt", encoding="utf-8").read()
add24 = open("font24_add.txt", encoding="utf-8").read()


def insert(table, extra):
    """在指定表的结尾 }; 之前插入新条目"""
    global s
    m = re.search(r"const\s+\w+\s+%s\[\]\s*=\s*\{" % table, s)
    if not m:
        print("找不到表:", table)
        return
    start = m.end()
    end = s.find("\n};", start)
    if end < 0:
        print("找不到表尾:", table)
        return
    body = s[start:end]
    # 去重：已经存在的字跳过
    lines = []
    for line in extra.strip().splitlines():
        ch = re.match(r'\s*"([^"]+)"', line)
        if ch and ('"%s"' % ch.group(1)) in body:
            continue
        lines.append(line)
    if not lines:
        print(table, "无需新增")
        return
    s = s[:end] + "\n" + "\n".join(lines) + s[end:]
    print(table, "新增", len(lines), "个")


insert("tfont16", add16)
insert("tfont24", add24)
insert("tfont12", add16)

open(H, "w", encoding="utf-8").write(s)

# 统计
chars = sorted(set(re.findall(r"[\u4e00-\u9fff]", s)))
print("现在字库共 %d 个汉字:" % len(chars))
print("".join(chars))
