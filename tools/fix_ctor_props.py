import re
import sys
from pathlib import Path

PARAM_PROP = re.compile(r'^(?:public|private|protected|readonly)\s+([A-Za-z_]\w*)\s*:\s*(.+)$', re.S)


def split_params(text):
    parts, depth, cur = [], 0, ''
    for ch in text:
        if ch in '<[({':
            depth += 1
        elif ch in '>])}':
            depth -= 1
        if ch == ',' and depth == 0:
            parts.append(cur)
            cur = ''
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    return parts


def transform(path: Path) -> int:
    src = path.read_text(encoding='utf-8')
    out = []
    changed = 0
    i = 0
    n = len(src)
    while i < n:
        m = re.match(r'constructor\s*\(', src[i:])
        if not m:
            out.append(src[i])
            i += 1
            continue
        start = i
        j = i + m.end()
        depth = 1
        while j < n and depth > 0:
            if src[j] == '(':
                depth += 1
            elif src[j] == ')':
                depth -= 1
            j += 1
        params_text = src[i + m.end():j - 1]
        # skip if no parameter properties
        if not any(k in params_text for k in ('public ', 'private ', 'protected ', 'readonly ')):
            out.append(src[start:j])
            i = j
            continue
        params = split_params(params_text)
        fields, new_params = [], []
        for p in params:
            stripped = p.strip()
            pm = PARAM_PROP.match(stripped)
            if pm:
                name, ptype = pm.group(1), pm.group(2).strip()
                fields.append(f'  {name}: {ptype}\n')
                new_params.append(f'{name}: {ptype}')
            else:
                new_params.append(stripped)
        # indentation of the constructor line
        line_start = src.rfind('\n', 0, start) + 1
        indent = src[line_start:start]
        field_text = ''.join(indent + f.strip() + '\n' for f in fields) + '\n'
        out.append(field_text + indent + 'constructor(' + ', '.join(new_params) + ')')
        changed += 1
        i = j
    if changed:
        path.write_text(''.join(out), encoding='utf-8')
    return changed


total = 0
for root in sys.argv[1:]:
    for p in Path(root).rglob('*.ets'):
        if 'oh_modules' not in str(p) and '\\build\\' not in str(p):
            total += transform(p)
print(f'transformed constructors: {total}')
