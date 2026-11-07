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

ALLOW = ('已移除', '删除', '改为', '移除', '不再', '未申请', '无法申请', '无需', '不需要',
         'removed', 'replaced', 'no longer', 'not required')

problems = []
for rel, name in PROJECTS:
    base = os.path.join(ROOT, rel)
    tdir = os.path.join(base, 'entry', 'src', 'ohosTest', 'ets', 'test')
    code_names = []
    for f in sorted(os.listdir(tdir)):
        if f.endswith('.test.ets'):
            code_names += re.findall(r"^\s*it\('([^']+)'", io.open(os.path.join(tdir, f), encoding='utf-8').read(), re.M)

    doc = io.open(os.path.join(base, 'ohosTest.md'), encoding='utf-8').read()
    ui_part = doc.split('### UI 用例')[1].split('### 逻辑用例')[0]
    logic_part = doc.split('### 逻辑用例')[1]
    doc_all = re.findall(r'\| `([^`]+)` \|', ui_part) + re.findall(r'\| `([^`]+)` \|', logic_part)

    if sorted(doc_all) != sorted(code_names):
        problems.append('{}: 文档与代码用例不一致'.format(name))
    m = re.search(r'Tests run: (\d+)', doc)
    if not m or int(m.group(1)) != len(code_names):
        problems.append('{}: 文档结果数与实际用例数不符'.format(name))

    app_json = io.open(os.path.join(base, 'AppScope', 'app.json5'), encoding='utf-8').read()
    bundle = re.search(r'"bundleName"\s*:\s*"([^"]+)"', app_json).group(1)

    readme = io.open(os.path.join(base, 'README_zh.md'), encoding='utf-8').read()
    if 'API 26.0.0 适配说明' not in readme:
        problems.append(name + ': README_zh 缺少适配说明')
    m = re.search(r'共 (\d+) 个用例', readme)
    if not m or int(m.group(1)) != len(code_names):
        problems.append('{}: README_zh 用例数不符'.format(name))
    if bundle not in readme:
        problems.append('{}: README_zh 未包含正确 bundle {}'.format(name, bundle))

    en_path = os.path.join(base, 'README.md')
    if os.path.exists(en_path):
        en = io.open(en_path, encoding='utf-8').read()
        if 'API 26.0.0 Adaptation' not in en and 'API 26.0.0 适配说明' not in en:
            problems.append(name + ': README.md 缺少适配说明')

    for md in ('README_zh.md', 'README.md', 'ohosTest.md'):
        p = os.path.join(base, md)
        if not os.path.exists(p):
            continue
        text = io.open(p, encoding='utf-8').read()
        for token in ('subscribeSystemLiveView', 'userFileManager', 'setAudioScene',
                      'AbilityManager.updateConfiguration', 'README_MEDIA'):
            idx = 0
            while True:
                idx = text.find(token, idx)
                if idx == -1:
                    break
                ctx = text[max(0, idx - 120):idx + 120]
                if not any(k in ctx for k in ALLOW):
                    problems.append('{}: {} 存在未说明的旧接口引用 {}'.format(name, md, token))
                idx += len(token)

    print('{:26} cases={} bundle={}'.format(name, len(code_names), bundle))

print('')
print('== problems ==')
if problems:
    for p in sorted(set(problems)):
        print('-', p)
else:
    print('none')
