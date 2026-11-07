# -*- coding: utf-8 -*-
"""检查测试用例内声明但未使用的变量（规范：变量定义未使用视为无效测试）。"""
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
    for f in sorted(os.listdir(tdir)):
        if not f.endswith('.test.ets') or f == 'List.test.ets':
            continue
        text = io.open(os.path.join(tdir, f), encoding='utf-8').read()
        for m in re.finditer(r"^(\s*)it\('([^']+)'", text, re.M):
            indent = m.group(1)
            case = m.group(2)
            close = re.compile(r"^" + re.escape(indent) + r"\}\)", re.M).search(text, m.end())
            if not close:
                continue
            block = text[m.start():close.end()]
            for decl in re.finditer(r'^\s+(?:let|const)\s+(\w+)\s*[:=]', block, re.M):
                var = decl.group(1)
                if var in ('TAG',):
                    continue
                if len(re.findall(r'\b' + re.escape(var) + r'\b', block)) < 2:
                    problems.append('{} {}: 变量 {} 声明后未使用（用例 {}）'.format(
                        name, f, var, case))

print('== unused variable problems ==')
if problems:
    for p in problems:
        print('-', p)
else:
    print('none')
