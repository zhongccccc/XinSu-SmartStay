# -*- coding: utf-8 -*-
"""为缺少 expect 断言的用例补充有效断言（基于已有 assertComponentExist 的组件）。"""
import io
import os
import re

ROOT = r'D:\XTS\code\SystemFeature'
PROJECTS = [
    r'Notification\Publish',
    r'ResourceAllocation\ApplicationThemeSwitch',
    r'Media\GamePuzzle',
    r'WindowManagement\WindowManage',
    r'Security\CertificateFramework',
    r'Media\VoiceCallDemo',
    r'Media\Recorder',
    r'Media\MusicPlayer',
]

report = []
for rel in PROJECTS:
    tdir = os.path.join(ROOT, rel, 'entry', 'src', 'ohosTest', 'ets', 'test')
    for f in sorted(os.listdir(tdir)):
        if not f.endswith('.test.ets') or f == 'List.test.ets':
            continue
        path = os.path.join(tdir, f)
        text = io.open(path, encoding='utf-8').read()
        skipped = set()
        patched = 0
        while True:
            progress = False
            for m in re.finditer(r"^(\s*)it\('([^']+)'", text, re.M):
                indent = m.group(1)
                name = m.group(2)
                if name in skipped:
                    continue
                close_pat = re.compile(r"^" + re.escape(indent) + r"\}\)", re.M)
                cm = close_pat.search(text, m.end())
                if not cm:
                    continue
                block = text[m.start():cm.end()]
                if 'expect(' in block:
                    continue
                asserts = re.findall(r'assertComponentExist\((ON\.[^;]+?)\);', block)
                if not asserts:
                    skipped.add(name)
                    report.append(('SKIP', rel, f, name))
                    continue
                on_expr = asserts[-1]
                dm = re.search(r'await\s+(\w+)\.assertComponentExist', block)
                driver_var = dm.group(1) if dm else 'DRIVER'
                insert = (
                    "{i}  let assertedComponent = await {d}.findComponent({on});\n"
                    "{i}  expect(assertedComponent !== null).assertTrue();\n"
                ).format(i=indent, d=driver_var, on=on_expr)
                done_match = re.search(r'^' + re.escape(indent) + r"  done\(\);\n", block, re.M)
                if not done_match:
                    skipped.add(name)
                    report.append(('SKIP-NO-DONE', rel, f, name))
                    continue
                new_block = block[:done_match.start()] + insert + block[done_match.start():]
                text = text[:m.start()] + new_block + text[cm.end():]
                patched += 1
                progress = True
                break
            if not progress:
                break
        if patched:
            io.open(path, 'w', encoding='utf-8', newline='\n').write(text)
            report.append(('PATCHED', rel, f, str(patched)))

for r in report:
    print(r)
