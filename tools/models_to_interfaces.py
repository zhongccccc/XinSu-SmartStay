import re
import sys
from pathlib import Path

CLASS_RE = re.compile(r'export\s+class\s+(\w+)\s*\{')
FIELD_RE = re.compile(r'^\s*([A-Za-z_]\w*)\s*:\s*([^=\n]+?)\s*(?:=\s*.*)?$')


def convert(path: Path) -> int:
    src = path.read_text(encoding='utf-8')
    out = []
    i = 0
    n = len(src)
    changed = 0
    while i < n:
        m = CLASS_RE.search(src, i)
        if not m:
            out.append(src[i:])
            break
        out.append(src[i:m.start()])
        name = m.group(1)
        # find matching closing brace
        j = m.end()
        depth = 1
        while j < n and depth > 0:
            if src[j] == '{':
                depth += 1
            elif src[j] == '}':
                depth -= 1
            j += 1
        body = src[m.end():j - 1]
        # collect field declarations, skip constructor bodies
        fields = []
        k = 0
        blen = len(body)
        while k < blen:
            cm = re.match(r'\s*constructor\s*\(', body[k:])
            if cm:
                p = k + cm.end()
                depth2 = 1
                while p < blen and depth2 > 0:
                    if body[p] == '(':
                        depth2 += 1
                    elif body[p] == ')':
                        depth2 -= 1
                    p += 1
                # skip until matching brace of constructor body
                while p < blen and body[p] != '{':
                    p += 1
                depth3 = 1
                p += 1
                while p < blen and depth3 > 0:
                    if body[p] == '{':
                        depth3 += 1
                    elif body[p] == '}':
                        depth3 -= 1
                    p += 1
                k = p
                continue
            # read one line
            nl = body.find('\n', k)
            if nl == -1:
                nl = blen
            line = body[k:nl]
            fm = FIELD_RE.match(line)
            if fm:
                fields.append((fm.group(1), fm.group(2).strip()))
            k = nl + 1
        if not fields:
            out.append(src[m.start():j])
            i = j
            continue
        rendered = '\n'.join(f'  {fname}: {ftype}' for fname, ftype in fields)
        out.append(f'export interface {name} {{\n{rendered}\n}}')
        changed += 1
        i = j
    if changed:
        path.write_text(''.join(out), encoding='utf-8')
    return changed


total = 0
for root in sys.argv[1:]:
    for p in Path(root).rglob('*.ets'):
        if 'ohmodels' in str(p) or 'oh_modules' in str(p) or '\\build\\' not in str(p) and 'models' in str(p):
            pass
    for p in Path(root).rglob('*.ets'):
        if 'oh_modules' in str(p) or '\\build\\' in str(p):
            continue
        if 'models' not in str(p) and 'ThemeConst' not in str(p):
            continue
        total += convert(p)
print(f'converted classes: {total}')
