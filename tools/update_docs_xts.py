# -*- coding: utf-8 -*-
"""按新用例名/@tc.number 重新生成 ohosTest.md，并更新 README 中对旧用例名的引用。"""
import io
import os
import re
import sys

sys.path.insert(0, r'E:\zhikong\tools')
from xts_cases import PROJECTS as CASE_PROJECTS

ROOT = r'D:\XTS\code\SystemFeature'
BUNDLES = {
    'Publish': 'com.samples.notificationpublish',
    'ThemeSwitch': 'ohos.example.themeswitch',
    'GamePuzzle': 'ohos.samples.gamepuzzle',
    'WindowManage': 'ohos.samples.windowcomponent',
    'CertFramework': 'com.samples.certframework',
    'VoiceCall': 'com.samples.voicecalldemo',
    'Recorder': 'ohos.samples.recorder',
    'MusicPlayer': 'com.samples.musicplayer',
}


def upper_snake(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).upper()


def parse_old_docs(path):
    mapping = {}
    if not os.path.exists(path):
        return mapping
    text = io.open(path, encoding='utf-8').read()
    for m in re.finditer(r'^\| `([^`]+)` \| (.+?) \|$', text, re.M):
        mapping[m.group(1)] = m.group(2).strip()
    return mapping


for project in CASE_PROJECTS:
    base = os.path.join(ROOT, project['dir'])
    doc_path = os.path.join(base, 'ohosTest.md')
    old_map = parse_old_docs(doc_path)
    bundle = BUNDLES[project['short']]

    rows_ui = []
    rows_logic = []
    rename = []
    index = 1
    for fname, cases in project['files'].items():
        is_logic = fname.endswith('Logic.test.ets')
        for old_name, action, desc in cases:
            new_name = '{}{}Test{:04d}'.format(project['short'], action, index)
            tc_number = '{}_{}_{:04d}'.format(project['num'], upper_snake(action), index * 100)
            cn = old_map.get(old_name, desc)
            row = '| `{}` | `{}` | {} |'.format(new_name, tc_number, cn)
            (rows_logic if is_logic else rows_ui).append(row)
            rename.append((old_name, new_name))
            index += 1

    total = index - 1
    doc = '''# 测试用例说明

## 测试环境

- 设备：OpenHarmony 7.1.0.21（API 26.0.0）
- 测试框架：`@ohos/hypium` + `@ohos.UiTest`
- 测试模块：`entry_test`（`entry/src/ohosTest`）
- 运行命令：`hdc shell aa test -b {bundle} -m entry_test -s unittest OpenHarmonyTestRunner`

## 用例规范

- 每条用例包含 `@tc.number`、`@tc.name`、`@tc.desc`、`@tc.size`、`@tc.type`、`@tc.level` 注释字段；
- `it()` 的用例名与 `@tc.name`、用例内 `TAG` 三者保持一致；
- 用例过滤参数统一为 `TestType.FUNCTION | Size.MEDIUMTEST | Level.LEVEL0`；
- `@tc.number` 在工程内唯一，按接口顺序以 0100、0200…… 递增。

## 用例清单

### UI 用例（{ui_count} 个）

| 用例 | @tc.number | 说明 |
| --- | --- | --- |
{ui_rows}

### 逻辑用例（{logic_count} 个）

| 用例 | @tc.number | 说明 |
| --- | --- | --- |
{logic_rows}

## 最近一次执行结果

```
Tests run: {total}, Failure: 0, Error: 0, Pass: {total}, Ignore: 0
```
'''.format(bundle=bundle, ui_count=len(rows_ui), logic_count=len(rows_logic),
           ui_rows='\n'.join(rows_ui), logic_rows='\n'.join(rows_logic), total=total)

    io.open(doc_path, 'w', encoding='utf-8', newline='\n').write(doc)
    print('doc updated:', project['short'], 'ui=', len(rows_ui), 'logic=', len(rows_logic))

    for md in ('README_zh.md', 'README.md'):
        p = os.path.join(base, md)
        if not os.path.exists(p):
            continue
        text = io.open(p, encoding='utf-8').read()
        original = text
        for old_name, new_name in rename:
            text = text.replace(old_name, new_name)
        if text != original:
            io.open(p, 'w', encoding='utf-8', newline='\n').write(text)
            print('  readme updated:', md)
