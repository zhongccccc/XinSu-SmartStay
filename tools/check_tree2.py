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


def actual(base):
    s = set()
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in ('build', 'oh_modules', '.hvigor', '.git', 'node_modules')]
        s.update(files)
    return s


for rel, name in PROJECTS:
    base = os.path.join(ROOT, rel)
    files = actual(base)
    for md in ('README_zh.md', 'README.md'):
        p = os.path.join(base, md)
        if not os.path.exists(p):
            continue
        text = io.open(p, encoding='utf-8', errors='replace').read()
        for line in text.splitlines():
            mm = re.search(r'([A-Za-z0-9_][A-Za-z0-9_\-]*\.(?:ets|ts))\b', line)
            if not mm:
                continue
            item = mm.group(1)
            # 仅检查形如目录树/清单的行
            if not re.search(r'(\|\s*-+|\|\s{2,}|^---)', line):
                continue
            if item not in files:
                print('{} / {}: 列出的 {} 不存在'.format(name, md, item))
