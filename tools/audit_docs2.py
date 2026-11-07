# -*- coding: utf-8 -*-
import io
import os
import re

ROOT = r'D:\XTS\code\SystemFeature'
# (路径, 名称, bundle, UI用例数, 逻辑用例数, 原样例UI用例数)
PROJECTS = [
    (r'Notification\Publish', 'Publish', 'com.samples.notificationpublish', 2, 4, 1),
    (r'ResourceAllocation\ApplicationThemeSwitch', 'ApplicationThemeSwitch', 'ohos.example.themeswitch', 6, 5, 6),
    (r'Media\GamePuzzle', 'GamePuzzle', 'ohos.samples.gamepuzzle', 11, 5, 11),
    (r'WindowManagement\WindowManage', 'WindowManage', 'ohos.samples.windowcomponent', 13, 4, 13),
    (r'Security\CertificateFramework', 'CertificateFramework', 'com.samples.certframework', 10, 8, 10),
    (r'Media\VoiceCallDemo', 'VoiceCallDemo', 'com.samples.voicecalldemo', 5, 7, 5),
    (r'Media\Recorder', 'Recorder', 'ohos.samples.recorder', 14, 7, 14),
    (r'Media\MusicPlayer', 'MusicPlayer', 'com.samples.musicplayer', 4, 4, 1),
]

problems = []
print('== docs / config audit ==')
for rel, name, bundle, ui, logic, orig_ui in PROJECTS:
    base = os.path.join(ROOT, rel)
    total = ui + logic
    ok = True

    doc = os.path.join(base, 'ohosTest.md')
    if not os.path.exists(doc):
        problems.append(name + ': missing ohosTest.md')
        ok = False
    else:
        text = io.open(doc, encoding='utf-8').read()
        ui_part = text.split('### UI 用例')[1].split('### 逻辑用例')[0] if '### UI 用例' in text else ''
        logic_part = text.split('### 逻辑用例')[1] if '### 逻辑用例' in text else ''
        ui_rows = re.findall(r'^\| `[^`]+` \|', ui_part, re.M)
        logic_rows = re.findall(r'^\| `[^`]+` \|', logic_part, re.M)
        if len(ui_rows) != ui:
            problems.append('{}: ohosTest.md ui rows={} expected={}'.format(name, len(ui_rows), ui))
            ok = False
        if len(logic_rows) != logic:
            problems.append('{}: ohosTest.md logic rows={} expected={}'.format(name, len(logic_rows), logic))
            ok = False
        if 'Tests run: {}'.format(total) not in text:
            problems.append(name + ': ohosTest.md result count mismatch')
            ok = False

    readme = os.path.join(base, 'README_zh.md')
    rtext = io.open(readme, encoding='utf-8').read() if os.path.exists(readme) else ''
    if 'API 26.0.0 适配说明' not in rtext:
        problems.append(name + ': README_zh missing adaptation section')
        ok = False
    if '共 {} 个用例'.format(total) not in rtext:
        problems.append(name + ': README_zh case count mismatch (expect {})'.format(total))
        ok = False

    sig = os.path.join(base, 'signature')
    for f in ('app.cer', 'app.p12', 'app_profile.p7b'):
        if not os.path.exists(os.path.join(sig, f)):
            problems.append('{}: missing signature/{}'.format(name, f))
            ok = False

    bp = io.open(os.path.join(base, 'build-profile.json5'), encoding='utf-8').read()
    for token in ('"compileSdkVersion": "26.0.0"', '"compatibleSdkVersion": "26.0.0"',
                  '"targetSdkVersion": "26.0.0"', '"runtimeOS": "OpenHarmony"', '"signingConfigs"'):
        if token not in bp:
            problems.append('{}: build-profile missing {}'.format(name, token))
            ok = False

    for f in ('hvigorw', 'hvigorw.bat', os.path.join('hvigor', 'hvigor-wrapper.js')):
        if os.path.exists(os.path.join(base, f)):
            problems.append('{}: leftover {}'.format(name, f))
            ok = False

    ui_ok = ui >= orig_ui
    if not ui_ok:
        problems.append('{}: UI cases {} < original {}'.format(name, ui, orig_ui))
    print('{:26} ui={}/{} logic={} total={} ui_ge_original={} docs={}'.format(
        name, ui, orig_ui, logic, total, ui_ok, 'OK' if ok else 'FAIL'))

print('')
print('problems:')
if problems:
    for p in problems:
        print('-', p)
else:
    print('none')
