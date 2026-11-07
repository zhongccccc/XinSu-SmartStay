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
    mod = io.open(os.path.join(base, 'entry', 'src', 'main', 'module.json5'), encoding='utf-8', errors='replace').read()
    perms = re.findall(r'"name"\s*:\s*"(ohos\.permission\.[A-Z_]+)"', mod)
    readme = io.open(os.path.join(base, 'README_zh.md'), encoding='utf-8', errors='replace').read()

    missing_in_doc = [p for p in perms if p not in readme]
    if missing_in_doc:
        problems.append('{}: README_zh 未提及实际申请的权限 {}'.format(name, missing_in_doc))

    # 文档提到但代码未申请的权限（排除“已移除/不需要/无需”上下文）
    documented = re.findall(r'ohos\.permission\.[A-Z_]+', readme)
    for p in sorted(set(documented) - set(perms)):
        idx = readme.find(p)
        ctx = readme[max(0, idx - 60):idx + 40]
        if not any(k in ctx for k in ('移除', '不需要', '无需', '已随', '不再', '未申请', '无法申请')):
            problems.append('{}: README_zh 提到 {} 但 module.json5 未申请'.format(name, p))

    # 图片引用存在性（含 HTML img 标签）
    for md in ('README_zh.md', 'README.md', 'ohosTest.md'):
        path = os.path.join(base, md)
        if not os.path.exists(path):
            continue
        text = io.open(path, encoding='utf-8', errors='replace').read()
        refs = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', text) + re.findall(r'<img[^>]+src="([^"]+)"', text)
        for ref in refs:
            if ref.startswith('http'):
                continue
            target = os.path.normpath(os.path.join(base, ref))
            if not os.path.exists(target):
                problems.append('{}: {} 引用图片不存在 {}'.format(name, md, ref))

    print('{:26} perms={}'.format(name, perms if perms else '[]'))

print('')
print('== problems ==')
if problems:
    for p in problems:
        print('-', p)
else:
    print('none')
