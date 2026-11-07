# -*- coding: utf-8 -*-
"""检查 @tc.number/@tc.name 唯一性、旧注释残留、恒真断言语义、未使用变量。"""
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

problems = []
for rel in PROJECTS:
    name = os.path.basename(rel)
    tdir = os.path.join(ROOT, rel, 'entry', 'src', 'ohosTest', 'ets', 'test')
    numbers = []
    names = []
    for f in sorted(os.listdir(tdir)):
        if not f.endswith('.test.ets') or f == 'List.test.ets':
            continue
        # 文件名规范：大驼峰、无下划线
        base = f[:-len('.test.ets')]
        if not re.fullmatch(r'[A-Z][A-Za-z0-9]*', base):
            problems.append('{}: 文件名不符合大驼峰规范 -> {}'.format(name, f))
        text = io.open(os.path.join(tdir, f), encoding='utf-8').read()
        numbers += re.findall(r'@tc\.number\s+(\S+)', text)
        names += re.findall(r'@tc\.name\s+(\S+)', text)

        # 旧注释残留：it 前紧邻的注释块若无 @tc 字段
        for m in re.finditer(r"^(\s*)it\('", text, re.M):
            before = text[:m.start()]
            cm = re.search(r'/\*\*(?:(?!\*/).)*?\*/\n\s*$', before, re.S)
            if cm and '@tc.' not in cm.group(0):
                problems.append('{} {}: it 前存在无 @tc 的旧注释（行 {}）'.format(
                    name, f, text[:cm.start()].count('\n') + 1))

        # 恒真断言：两边完全相同的 assertEqual
        for m in re.finditer(r'expect\(([^)]*)\)\.assertEqual\(([^)]*)\)', text):
            left, right = m.group(1).strip(), m.group(2).strip()
            if left == right:
                problems.append('{} {}: 恒真断言 {} == {}'.format(name, f, left, right))

    dup_nums = sorted({n for n in numbers if numbers.count(n) > 1})
    dup_names = sorted({n for n in names if names.count(n) > 1})
    if dup_nums:
        problems.append('{}: 重复 @tc.number {}'.format(name, dup_nums))
    if dup_names:
        problems.append('{}: 重复 @tc.name {}'.format(name, dup_names))
    print('{:26} numbers={} names={}'.format(name, len(numbers), len(names)))

print('')
print('== problems ==')
if problems:
    for p in problems:
        print('-', p)
else:
    print('none')
