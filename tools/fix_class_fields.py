import re
import sys
from pathlib import Path

DEFAULT_BY_TYPE = [
    (r'^(string)$', "''"),
    (r'^(number)$', '0'),
    (r'^(boolean)$', 'false'),
]

field_re = re.compile(r'^(\s+)([A-Za-z_]\w*)\s*:\s*([A-Za-z_][\w$.]*(?:<[^>]*>)?(?:\[\])?)\s*$')
class_re = re.compile(r'^\s*(?:export\s+)?(?:default\s+)?(class|interface|struct|enum)\b')


def fix_file(path: Path) -> int:
    lines = path.read_text(encoding='utf-8').splitlines(keepends=True)
    out = []
    stack = []
    depth = 0
    changed = 0
    for line in lines:
        stripped = line.strip()
        m = class_re.match(line)
        if m:
            stack.append((depth, m.group(1)))
        fm = field_re.match(line.rstrip('\n'))
        if fm and stack and stack[-1][1] == 'class':
            indent, name, ftype = fm.groups()
            default = None
            for pattern, value in DEFAULT_BY_TYPE:
                if re.match(pattern, ftype):
                    default = value
                    break
            newline = line
            if default is not None:
                newline = f'{indent}{name}: {ftype} = {default}\n'
            else:
                newline = f'{indent}{name}: {ftype} | undefined = undefined\n'
            if newline != line:
                changed += 1
                line = newline
        out.append(line)
        depth += line.count('{') - line.count('}')
        while stack and depth <= stack[-1][0]:
            stack.pop()
    if changed:
        path.write_text(''.join(out), encoding='utf-8')
    return changed


total = 0
for root in sys.argv[1:]:
    for p in Path(root).rglob('*'):
        if p.suffix in ('.ets', '.ts') and 'oh_modules' not in str(p) and '\\build\\' not in str(p):
            total += fix_file(p)
print(f'changed lines: {total}')
