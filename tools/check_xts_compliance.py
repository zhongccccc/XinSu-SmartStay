# -*- coding: utf-8 -*-
"""检查 XTS 测试用例规范符合性：@tc 字段、命名一致、行宽、断言、catch、恒真断言。"""
import io
import os
import re

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

MAX_LINE = 120
problems = []
summary = []

for rel in PROJECTS:
    name = os.path.basename(rel)
    tdir = os.path.join(ROOT, rel, 'entry', 'src', 'ohosTest', 'ets', 'test')
    cases = 0
    for f in sorted(os.listdir(tdir)):
        if not f.endswith('.test.ets') or f == 'List.test.ets':
            continue
        path = os.path.join(tdir, f)
        text = io.open(path, encoding='utf-8').read()
        lines = text.splitlines()

        # 1) it 用例：前必须有 @tc.number/@tc.name/@tc.desc，名称一致
        for m in re.finditer(r"^\s*it\('([^']+)',\s*TestType", text, re.M):
            cases += 1
            case_name = m.group(1)
            before = text[:m.start()]
            block = before[-700:]
            if '@tc.number' not in block or '@tc.name' not in block or '@tc.desc' not in block:
                problems.append('{} {}: 缺少 @tc 注释 -> {}'.format(name, f, case_name))
            nm = re.search(r'@tc\.name\s+(\S+)', block)
            if not nm or nm.group(1) != case_name:
                problems.append('{} {}: @tc.name 与 it 名称不一致 -> {}'.format(name, f, case_name))
            tag = re.search(r"const TAG = '([^']+)'", text[m.start():m.start() + 400])
            if not tag or tag.group(1) != case_name:
                problems.append('{} {}: TAG 与用例名不一致 -> {}'.format(name, f, case_name))
            if 'console.log(TAG' not in text[m.start():m.start() + 600]:
                problems.append('{} {}: 缺少 TAG 日志 -> {}'.format(name, f, case_name))

        # 2) 行宽
        for i, line in enumerate(lines, 1):
            if len(line) > MAX_LINE:
                problems.append('{} {}:{} 行宽 {} > {}'.format(name, f, i, len(line), MAX_LINE))

        # 3) catch 中必须有断言
        for cm in re.finditer(r'\} catch \([^)]*\) \{', text):
            seg = text[cm.end():cm.end() + 400]
            body = seg.split('\n  }')[0]
            if 'expect(' not in body:
                problems.append('{} {}: catch 中缺少断言（行 {}）'.format(
                    name, f, text[:cm.start()].count('\n') + 1))

        # 4) 恒真断言
        for pat in (r'expect\(\s*true\s*\)', r'expect\(\s*1\s*\)\.assertEqual\(\s*1\s*\)',
                    r'expect\(\s*0\s*\)\.assertEqual\(\s*0\s*\)'):
            for hm in re.finditer(pat, text):
                problems.append('{} {}: 疑似恒真断言 -> {}'.format(
                    name, f, hm.group(0)))

        # 5) 每个 it 内必须有 expect
        blocks = re.split(r"^\s*it\('", text, flags=re.M)[1:]
        for b in blocks:
            head = b.split("'")[0]
            if 'expect(' not in b.split('\n})')[0]:
                problems.append('{} {}: 用例 {} 缺少断言'.format(name, f, head))

    summary.append((name, cases))

print('== summary ==')
for n, c in summary:
    print('{:26} cases={}'.format(n, c))
print('')
print('== problems ==')
if problems:
    for p in problems:
        print('-', p)
else:
    print('none')
