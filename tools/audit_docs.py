# -*- coding: utf-8 -*-
import io
import os
import re

ROOT = r'D:\XTS\code\SystemFeature'
PROJECTS = [
    (r'Notification\Publish', 'Publish', 'com.samples.notificationpublish', 6),
    (r'ResourceAllocation\ApplicationThemeSwitch', 'ApplicationThemeSwitch', 'ohos.example.themeswitch', 11),
    (r'Media\GamePuzzle', 'GamePuzzle', 'ohos.samples.gamepuzzle', 8),
    (r'WindowManagement\WindowManage', 'WindowManage', 'ohos.samples.windowcomponent', 8),
    (r'Security\CertificateFramework', 'CertificateFramework', 'com.samples.certframework', 18),
    (r'Media\VoiceCallDemo', 'VoiceCallDemo', 'com.samples.voicecalldemo', 10),
    (r'Media\Recorder', 'Recorder', 'ohos.samples.recorder', 10),
    (r'Media\MusicPlayer', 'MusicPlayer', 'com.samples.musicplayer', 8),
]

problems = []
print('== docs / config audit ==')
for rel, name, bundle, expected in PROJECTS:
    base = os.path.join(ROOT, rel)
    ok = True
    # ohosTest.md
    doc = os.path.join(base, 'ohosTest.md')
    if not os.path.exists(doc):
        problems.append(name + ': missing ohosTest.md')
        ok = False
    else:
        text = io.open(doc, encoding='utf-8').read()
        rows = re.findall(r'^\| `[^`]+` \|', text, re.M)
        if len(rows) != expected:
            problems.append('{}: ohosTest.md rows={} expected={}'.format(name, len(rows), expected))
            ok = False
        if 'Tests run: {}'.format(expected) not in text:
            problems.append(name + ': ohosTest.md result count mismatch')
            ok = False
        if '逻辑用例' not in text:
            problems.append(name + ': ohosTest.md missing logic section')
            ok = False
    # README_zh.md
    readme = os.path.join(base, 'README_zh.md')
    if not os.path.exists(readme):
        problems.append(name + ': missing README_zh.md')
        ok = False
    else:
        rtext = io.open(readme, encoding='utf-8').read()
        if 'API 26.0.0 适配说明' not in rtext:
            problems.append(name + ': README_zh missing adaptation section')
            ok = False
        if '共 {} 个用例'.format(expected) not in rtext:
            problems.append(name + ': README_zh case count mismatch')
            ok = False
    # signature
    sig = os.path.join(base, 'signature')
    for f in ('app.cer', 'app.p12', 'app_profile.p7b'):
        if not os.path.exists(os.path.join(sig, f)):
            problems.append('{}: missing signature/{}'.format(name, f))
            ok = False
    # build-profile
    bp = io.open(os.path.join(base, 'build-profile.json5'), encoding='utf-8').read()
    for token in ('"compileSdkVersion": "26.0.0"', '"compatibleSdkVersion": "26.0.0"',
                  '"targetSdkVersion": "26.0.0"', '"runtimeOS": "OpenHarmony"', '"signingConfigs"'):
        if token not in bp:
            problems.append('{}: build-profile missing {}'.format(name, token))
            ok = False
    # leftover wrapper
    for f in ('hvigorw', 'hvigorw.bat', os.path.join('hvigor', 'hvigor-wrapper.js')):
        if os.path.exists(os.path.join(base, f)):
            problems.append('{}: leftover {}'.format(name, f))
            ok = False
    print('{:26} docs={} cases={}'.format(name, 'OK' if ok else 'FAIL', expected))

print('')
print('== template test leftovers ==')
found = False
for rel, name, bundle, expected in PROJECTS:
    tdir = os.path.join(ROOT, rel, 'entry', 'src', 'ohosTest', 'ets', 'test')
    for f in os.listdir(tdir):
        p = os.path.join(tdir, f)
        if not os.path.isfile(p):
            continue
        text = io.open(p, encoding='utf-8', errors='replace').read()
        if 'assertContain' in text or "let a = 'abc'" in text:
            print('{}: template leftovers in {}'.format(name, f))
            found = True
if not found:
    print('none')

print('')
print('== logic test files ==')
for rel, name, bundle, expected in PROJECTS:
    tdir = os.path.join(ROOT, rel, 'entry', 'src', 'ohosTest', 'ets', 'test')
    logic = [f for f in os.listdir(tdir) if 'Logic' in f]
    lt = io.open(os.path.join(tdir, 'List.test.ets'), encoding='utf-8').read()
    wired = any(f.replace('.test.ets', '') in lt for f in logic)
    print('{:26} logic_files={} wired={}'.format(name, logic, wired))
    if not wired:
        problems.append(name + ': logic suite not wired')

print('')
print('== problems ==')
if problems:
    for p in problems:
        print('-', p)
else:
    print('none')
