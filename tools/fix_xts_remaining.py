# -*- coding: utf-8 -*-
"""修复剩余规范问题：长行换行、Certificate chain 用例断言、WindowManage 导入换行。"""
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

# 1) Certificate chain 用例补充断言
cert_test = os.path.join(ROOT, r'Security\CertificateFramework', 'entry', 'src', 'ohosTest', 'ets', 'test',
                         'CertFrameworkLogic.test.ets')
text = io.open(cert_test, encoding='utf-8').read()
old = """      let chainModel = new CertChainModel();
      await chainModel.createX509CertChain();
      done();
"""
new = """      let chainModel = new CertChainModel();
      let validateResult = await chainModel.validate(false);
      expect(validateResult.code).assertEqual(200);
      done();
"""
assert old in text
text = text.replace(old, new)
io.open(cert_test, 'w', encoding='utf-8', newline='\n').write(text)
print('cert chain case patched')

# 2) WindowManageLogic 导入换行
wm = os.path.join(ROOT, r'WindowManagement\WindowManage', 'entry', 'src', 'ohosTest', 'ets', 'test',
                  'WindowManageLogic.test.ets')
text = io.open(wm, encoding='utf-8').read()
old_import = "import { WindowEventId, WindowColor, WindowType } from '../../../../../WindowComponent/src/main/ets/components/util/WindowConst';"
new_import = ("import {\n  WindowEventId,\n  WindowColor,\n  WindowType\n"
              "} from '../../../../../WindowComponent/src/main/ets/components/util/WindowConst';")
if old_import in text:
    text = text.replace(old_import, new_import)
    io.open(wm, 'w', encoding='utf-8', newline='\n').write(text)
    print('windowmanage import wrapped')

# 3) 长行换行：在 "(ON." 处折行
for rel in PROJECTS:
    tdir = os.path.join(ROOT, rel, 'entry', 'src', 'ohosTest', 'ets', 'test')
    for f in sorted(os.listdir(tdir)):
        if not f.endswith('.test.ets'):
            continue
        path = os.path.join(tdir, f)
        lines = io.open(path, encoding='utf-8').read().splitlines()
        changed = False
        out = []
        for line in lines:
            if len(line) > 120 and '(ON.' in line:
                idx = line.index('(ON.')
                indent = len(line) - len(line.lstrip())
                first = line[:idx + 1]
                second = ' ' * (indent + 4) + line[idx + 1:]
                out.append(first)
                out.append(second)
                changed = True
            else:
                out.append(line)
        if changed:
            io.open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
            print('wrapped', rel, f)
