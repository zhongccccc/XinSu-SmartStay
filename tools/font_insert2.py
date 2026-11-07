import re

H = "lcd_font.h"
bak = "lcd_font.h.bak"

# 从备份恢复，只插 16 与 24
s = open(bak, encoding="utf-8", errors="replace").read()
add16 = open("font16_add.txt", encoding="utf-8").read()
add24 = open("font24_add.txt", encoding="utf-8").read()


def insert(table, extra):
    global s
    m = re.search(r"const\s+\w+\s+%s\[\]\s*=\s*\{" % table, s)
    if not m:
        print("找不到表:", table)
        return
    start = m.end()
    end = s.find("\n};", start)
    body = s[start:end]
    lines = []
    for line in extra.strip().splitlines():
        ch = re.match(r'\s*"([^"]+)"', line)
        if ch and ('"%s"' % ch.group(1)) in body:
            continue
        lines.append(line)
    s = s[:end] + "\n" + "\n".join(lines) + s[end:]
    print(table, "新增", len(lines))


insert("tfont16", add16)
insert("tfont24", add24)
open(H, "w", encoding="utf-8").write(s)

chars = sorted(set(re.findall(r"[\u4e00-\u9fff]", s)))
print("字库汉字数:", len(chars))
print("".join(chars))
