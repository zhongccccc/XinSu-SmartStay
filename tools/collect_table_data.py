# -*- coding: utf-8 -*-
"""汇总 9 个工程的用例数据与代码改动量。"""
import io
import os
import re
import subprocess

ROOT = r'D:\XTS\code\SystemFeature'
GIT = r'D:\XTS'
PROJECTS = [
    ('74', r'Media\Camera'),
    ('75', r'Media\GamePuzzle'),
    ('76', r'Media\MusicPlayer'),
    ('77', r'Media\Recorder'),
    ('78', r'Media\VoiceCallDemo'),
    ('79', r'Notification\Publish'),
    ('80', r'ResourceAllocation\ApplicationThemeSwitch'),
    ('81', r'Security\CertificateFramework'),
    ('82', r'WindowManagement\WindowManage'),
]

TEXT_EXT = ('.ets', '.ts', '.js', '.json', '.json5', '.md', '.txt', '.jsonc')
SKIP = ('oh_modules', 'build', '.hvigor', '.idea', 'signature', 'node_modules', 'oh-package-lock.json5')


def git(*args):
    out = subprocess.run(['git', '-C', GIT] + list(args), capture_output=True, text=True,
                         encoding='utf-8', errors='replace')
    return out.stdout


for num, rel in PROJECTS:
    base = os.path.join(ROOT, rel)
    tdir = os.path.join(base, 'entry', 'src', 'ohosTest', 'ets', 'test')
    ui_cases = logic_cases = 0
    logic_files = 0
    logic_lines = 0
    for name in sorted(os.listdir(tdir)):
        if not name.endswith('.test.ets'):
            continue
        text = io.open(os.path.join(tdir, name), encoding='utf-8').read()
        cases = len(re.findall(r'@tc\.number', text))
        if 'Logic' in name:
            logic_cases += cases
            logic_files += 1
            logic_lines += text.count('\n') + 1
        else:
            ui_cases += cases

    # 跟踪文件改动
    gitpath = 'code/SystemFeature/' + rel.replace('\\', '/')
    stat = git('diff', '--numstat', '--', gitpath)
    add = dele = files = 0
    for line in stat.splitlines():
        parts = line.split('\t')
        if len(parts) >= 3:
            try:
                add += int(parts[0])
                dele += int(parts[1])
                files += 1
            except ValueError:
                pass

    # 未跟踪文本文件
    status = git('status', '--porcelain', '--', gitpath)
    untracked = 0
    untracked_lines = 0
    for line in status.splitlines():
        if not line.startswith('??'):
            continue
        path = line[3:].strip()
        if any(s in path for s in SKIP) or not path.endswith(TEXT_EXT):
            continue
        full = os.path.join(GIT, path)
        if os.path.isfile(full):
            untracked += 1
            untracked_lines += io.open(full, encoding='utf-8', errors='replace').read().count('\n') + 1

    print('{}\t{}\tUI={}\tlogic={}\tlogicFiles={}\tlogicLines={}\tdiffFiles={}\t+{}\t-{}\tuntrackedFiles={}\tuntrackedLines={}'.format(
        num, rel, ui_cases, logic_cases, logic_files, logic_lines, files, add, dele, untracked, untracked_lines))
