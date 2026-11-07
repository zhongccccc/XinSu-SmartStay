# -*- coding: utf-8 -*-
import io
import os
import re

ROOT = r'D:\XTS\code\SystemFeature'
PROJECTS = [
    (r'Notification\Publish', 'Publish'),
    (r'ResourceAllocation\ApplicationThemeSwitch', 'ApplicationThemeSwitch'),
    (r'Media\GamePuzzle', 'GamePuzzle'),
    (r'WindowManagement\WindowManage', 'WindowManage'),
    (r'Security\CertificateFramework', 'CertificateFramework'),
    (r'Media\VoiceCallDemo', 'VoiceCallDemo'),
    (r'Media\Recorder', 'Recorder'),
    (r'Media\MusicPlayer', 'MusicPlayer'),
]


def actual_files(base):
    found = set()
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in ('build', 'oh_modules', '.hvigor', '.git', 'node_modules')]
        for f in files:
            found.add(f)
    return found


problems = []
for rel, name in PROJECTS:
    base = os.path.join(ROOT, rel)
    files = actual_files(base)
    for md in ('README_zh.md', 'README.md'):
        path = os.path.join(base, md)
        if not os.path.exists(path):
            continue
        text = io.open(path, encoding='utf-8', errors='replace').read()
        m = re.search(r'###?\s*工程目录[\s\S]{0,200}?```[\s\S]*?```', text)
        if not m:
            m = re.search(r'###?\s*Project Directory[\s\S]{0,200}?```[\s\S]*?```', text)
        block = m.group(0) if m else ''
        for line in block.splitlines():
            line = line.strip().lstrip('|').lstrip('-').strip()
            mm = re.match(r'([A-Za-z0-9_][A-Za-z0-9_\-]*(?:\.[A-Za-z0-9_\-]+)*\.(?:ets|ts|json5|json|js))$', line.split('//')[0].strip())
            if mm:
                item = mm.group(1)
                if item not in files:
                    problems.append('{}: {} 工程目录列出 {} 但工程中不存在'.format(name, md, item))

print('== directory listing problems ==')
if problems:
    for p in sorted(set(problems)):
        print('-', p)
else:
    print('none')
