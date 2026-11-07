# -*- coding: utf-8 -*-
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

problems = []
for rel in PROJECTS:
    name = os.path.basename(rel)
    tdir = os.path.join(ROOT, rel, 'entry', 'src', 'ohosTest', 'ets', 'test')
    names = []
    suites = []
    for f in sorted(os.listdir(tdir)):
        if not f.endswith('.test.ets'):
            continue
        text = io.open(os.path.join(tdir, f), encoding='utf-8').read()
        for m in re.finditer(r"^\s*describe\('([^']*)'", text, re.M):
            suites.append(m.group(1))
        for m in re.finditer(r"^\s*it\((.+?),\s*\d+,\s*(?:async\s*)?\(", text, re.M):
            expr = m.group(1).strip()
            # 只接受纯字符串字面量
            lit = re.fullmatch(r"'([^']*)'", expr)
            if not lit:
                problems.append('{}: non-literal case name -> {}'.format(name, expr))
                names.append(expr)
            else:
                names.append(lit.group(1))
    dups = sorted({n for n in names if names.count(n) > 1})
    if dups:
        problems.append('{}: duplicate case names {}'.format(name, dups))
    sdups = sorted({s for s in suites if suites.count(s) > 1})
    if sdups:
        problems.append('{}: duplicate suite names {}'.format(name, sdups))
    print('{:26} suites={} cases={} unique={}'.format(name, suites, len(names), len(set(names))))

print('')
print('problems:')
if problems:
    for p in problems:
        print('-', p)
else:
    print('none')
