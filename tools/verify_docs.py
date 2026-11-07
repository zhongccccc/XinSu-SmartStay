# -*- coding: utf-8 -*-
import io
import os
import sys

ROOT = r'D:\XTS\code\SystemFeature'
PROJECT_DIRS = [
    r'Notification\Publish',
    r'ResourceAllocation\ApplicationThemeSwitch',
    r'Media\GamePuzzle',
    r'WindowManagement\WindowManage',
    r'Security\CertificateFramework',
    r'Media\VoiceCallDemo',
    r'Media\Recorder',
    r'Media\MusicPlayer',
]

MARKERS = ['测试用例说明', 'API 26.0.0 适配说明', '用例列表', '编译与运行']

for d in PROJECT_DIRS:
    base = os.path.join(ROOT, d)
    name = os.path.basename(d)
    for fname in ('README_zh.md', 'ohosTest.md'):
        path = os.path.join(base, fname)
        if not os.path.exists(path):
            print('{}/{}: MISSING'.format(name, fname))
            continue
        raw = io.open(path, 'rb').read()
        try:
            text = raw.decode('utf-8')
            ok_utf8 = True
        except UnicodeDecodeError:
            text = raw.decode('utf-8', errors='replace')
            ok_utf8 = False
        bad = text.count('\ufffd')
        found = [m for m in MARKERS if m in text]
        print('{}/{}: utf8={} replacement_chars={} markers={} chars={}'.format(
            name, fname, ok_utf8, bad, len(found), len(text)))
