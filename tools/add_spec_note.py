# -*- coding: utf-8 -*-
"""在各工程 README 的测试章节补充 XTS 用例规范说明。"""
import io
import os

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

NOTE = ('用例遵循 XTS 编码规范：每条用例均包含 `@tc.number`、`@tc.name`、`@tc.desc`、`@tc.size`、`@tc.type`、`@tc.level`，'
        '`it()` 用例名与 `@tc.name`、用例内 `TAG` 保持一致，过滤参数统一为 '
        '`TestType.FUNCTION | Size.MEDIUMTEST | Level.LEVEL0`。\n\n')

for rel in PROJECTS:
    for md in ('README_zh.md',):
        p = os.path.join(ROOT, rel, md)
        if not os.path.exists(p):
            continue
        text = io.open(p, encoding='utf-8').read()
        if 'XTS 编码规范' in text:
            continue
        marker = '### 测试\n\n'
        if marker in text:
            text = text.replace(marker, marker + NOTE, 1)
            io.open(p, 'w', encoding='utf-8', newline='\n').write(text)
            print('note added:', rel, md)
        else:
            print('marker not found:', rel)
