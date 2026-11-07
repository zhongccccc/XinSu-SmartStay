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


def read(path):
    return io.open(path, encoding='utf-8', errors='replace').read()


for rel, name in PROJECTS:
    base = os.path.join(ROOT, rel)
    # ---- actual test case names from code ----
    tdir = os.path.join(base, 'entry', 'src', 'ohosTest', 'ets', 'test')
    code_names = []
    code_suites = []
    for f in sorted(os.listdir(tdir)):
        if not f.endswith('.test.ets'):
            continue
        text = read(os.path.join(tdir, f))
        code_suites += re.findall(r"describe\('([^']+)'", text)
        code_names += re.findall(r"^\s*it\('([^']+)'", text, re.M)

    # ---- docs ----
    doc_path = os.path.join(base, 'ohosTest.md')
    doc = read(doc_path)
    ui_part = doc.split('### UI 用例')[1].split('### 逻辑用例')[0] if '### UI 用例' in doc else ''
    logic_part = doc.split('### 逻辑用例')[1] if '### 逻辑用例' in doc else ''
    doc_ui = re.findall(r'\| `([^`]+)` \|', ui_part)
    doc_logic = re.findall(r'\| `([^`]+)` \|', logic_part)
    doc_all = doc_ui + doc_logic

    if sorted(doc_all) != sorted(code_names):
        problems.append('{}: ohosTest.md 与代码用例不一致\n  仅文档有: {}\n  仅代码有: {}'.format(
            name, sorted(set(doc_all) - set(code_names)), sorted(set(code_names) - set(doc_all))))
    if len(doc_ui) != len(set(doc_ui)) or len(doc_logic) != len(set(doc_logic)):
        problems.append(name + ': ohosTest.md 存在重复用例行')
    m = re.search(r'Tests run: (\d+)', doc)
    if not m:
        problems.append(name + ': ohosTest.md 缺少 Tests run 结果')
    elif int(m.group(1)) != len(code_names):
        problems.append('{}: ohosTest.md 结果数 {} != 实际用例数 {}'.format(name, m.group(1), len(code_names)))

    # ---- bundle ----
    app_json = read(os.path.join(base, 'AppScope', 'app.json5'))
    bundle = re.search(r'"bundleName"\s*:\s*"([^"]+)"', app_json).group(1)

    readme_zh = read(os.path.join(base, 'README_zh.md'))
    if 'API 26.0.0 适配说明' not in readme_zh:
        problems.append(name + ': README_zh.md 缺少适配说明章节')
    m = re.search(r'共 (\d+) 个用例', readme_zh)
    if not m:
        problems.append(name + ': README_zh.md 缺少用例总数说明')
    elif int(m.group(1)) != len(code_names):
        problems.append('{}: README_zh.md 用例总数 {} != 实际 {}'.format(name, m.group(1), len(code_names)))
    if bundle not in readme_zh:
        problems.append('{}: README_zh.md 未出现正确 bundle（{}）'.format(name, bundle))
    if 'aa test -b' in readme_zh and bundle not in readme_zh.split('aa test -b')[1][:120]:
        problems.append(name + ': README_zh.md 测试命令 bundle 可能不正确')

    # ---- image links in docs ----
    for doc_name in ('README_zh.md', 'README.md', 'ohosTest.md'):
        p = os.path.join(base, doc_name)
        if not os.path.exists(p):
            continue
        text = read(p)
        for img in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', text):
            if img.startswith('http'):
                continue
            target = os.path.normpath(os.path.join(base, img))
            if not os.path.exists(target):
                problems.append('{}: {} 引用了不存在的图片 {}'.format(name, doc_name, img))

    # ---- english readme ----
    en = os.path.join(base, 'README.md')
    if os.path.exists(en):
        en_text = read(en)
        if 'API 26.0.0 Adaptation' not in en_text:
            problems.append(name + ': README.md 缺少 Adaptation 章节')

    # ---- stale/removed feature mentions outside adaptation context ----
    removed = ['subscribeSystemLiveView', 'userFileManager', 'setAudioScene', 'AbilityManager.updateConfiguration']
    for token in removed:
        for doc_name in ('README_zh.md', 'README.md', 'ohosTest.md'):
            p = os.path.join(base, doc_name)
            if not os.path.exists(p):
                continue
            text = read(p)
            if token in text:
                # 出现在适配说明/迁移说明中可接受
                idx = text.find(token)
                context = text[max(0, idx - 80):idx + 80]
                if ('已移除' not in context and '删除' not in context and '改为' not in context
                        and 'removed' not in context.lower() and 'replaced' not in context.lower()):
                    problems.append('{}: {} 中出现待确认的旧 API 引用: {}'.format(name, doc_name, token))

    print('{:26} code={} doc={} (ui={} logic={}) bundle={}'.format(
        name, len(code_names), len(doc_all), len(doc_ui), len(doc_logic), bundle))

print('')
print('== problems ==')
if problems:
    for p in problems:
        print('-', p)
else:
    print('none')
