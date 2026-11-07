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

problems = []
for rel, name in PROJECTS:
    base = os.path.join(ROOT, rel)
    for md in ('README_zh.md', 'README.md', 'ohosTest.md'):
        path = os.path.join(base, md)
        if not os.path.exists(path):
            continue
        text = io.open(path, encoding='utf-8', errors='replace').read()

        # 1) markdown 本地链接
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if target.startswith('http') or target.startswith('#') or target.startswith('mailto'):
                continue
            t = target.split('#')[0].strip()
            if not t:
                continue
            if not os.path.exists(os.path.normpath(os.path.join(base, t))):
                problems.append('{}: {} 链接不存在 -> {}'.format(name, md, target))

        # 2) 反引号中的工程内路径
        for code_path in re.findall(r'`([A-Za-z0-9_\-./]+\.(?:ets|ts|json5|json|js|md|jpeg|png|gif|mp4))`', text):
            if code_path.startswith('http'):
                continue
            if not os.path.exists(os.path.normpath(os.path.join(base, code_path))):
                problems.append('{}: {} 反引号路径不存在 -> {}'.format(name, md, code_path))

print('== link / path problems ==')
if problems:
    for p in sorted(set(problems)):
        print('-', p)
else:
    print('none')
