# -*- coding: utf-8 -*-
"""按 XTS 编码规范改造测试用例（v2：修正缩进、合并/清理旧注释）。"""
import io
import os
import re

ROOT = r'D:\XTS\code\SystemFeature'

# 复用 v1 的映射，单独存放于 xts_cases.py
from xts_cases import PROJECTS


def upper_snake(name):
    s = re.sub(r'(?<!^)(?=[A-Z])', '_', name)
    return s.upper()


def transform_file(path, project, file_cases, index_start):
    text = io.open(path, encoding='utf-8').read()
    # 1) 补充 hypium 导入
    m = re.search(r"import \{([^}]+)\} from '@ohos/hypium';", text)
    if m:
        names = [n.strip() for n in m.group(1).split(',') if n.strip()]
        for extra in ('TestType', 'Size', 'Level'):
            if extra not in names:
                names.append(extra)
        text = text[:m.start()] + "import { " + ', '.join(names) + " } from '@ohos/hypium';" + text[m.end():]

    idx = index_start
    for old_name, action, desc in file_cases:
        new_name = '{}{}Test{:04d}'.format(project['short'], action, idx)
        tc_number = '{}_{}_{:04d}'.format(project['num'], upper_snake(action), idx * 100)
        pattern = re.compile(
            r"^(\s*)it\('" + re.escape(old_name) + r"',\s*0,\s*(async\s*\(done: Function\)|\(\))\s*=>\s*\{",
            re.M)
        mm = pattern.search(text)
        if not mm:
            print('  MISS it:', old_name)
            idx += 1
            continue
        indent = mm.group(1)
        body_indent = indent + '  '
        is_async = mm.group(2).startswith('async')
        signature = (
            "it('{}', TestType.FUNCTION | Size.MEDIUMTEST | Level.LEVEL0,\n"
            "{}  {} => {{".format(
                new_name,
                indent,
                'async (done: () => void): Promise<void>' if is_async else '()'
            )
        )
        header = (
            "{i}/**\n"
            "{i} * @tc.number    {num}\n"
            "{i} * @tc.name      {name}\n"
            "{i} * @tc.desc      {desc}\n"
            "{i} * @tc.size      MediumTest\n"
            "{i} * @tc.type      Function\n"
            "{i} * @tc.level     Level 0\n"
            "{i} */\n"
            "{i}{sig}".format(i=indent, num=tc_number, name=new_name, desc=desc, sig=signature)
        )

        # 删除紧邻的旧注释（不含 @tc 字段）
        before = text[:mm.start()]
        old_comment = re.search(res := r'/\*\*(?:(?!\*/).)*?\*/\n\s*$', before, re.S)
        if old_comment:
            before = before[:old_comment.start()].rstrip(' \t')
        text = before + header + text[mm.end():]

        # 结束日志
        search_from = len(before) + len(header)
        close_pattern = re.compile(r"^" + re.escape(indent) + r"\}\)", re.M)
        cm = close_pattern.search(text, search_from)
        if cm:
            insert = "{i}  console.log(TAG + ' end');\n".format(i=indent)
            text = text[:cm.start()] + insert + text[cm.start():]

        # 开始日志：定位 signature 末尾的 {
        sig_pos = text.find(signature, len(before))
        brace_pos = text.find('{', sig_pos + len(signature) - 1)
        insert2 = "\n{i}const TAG = '{name}';\n{i}console.log(TAG + ' start');".format(
            i=body_indent, name=new_name)
        text = text[:brace_pos + 1] + insert2 + text[brace_pos + 1:]
        idx += 1
    io.open(path, 'w', encoding='utf-8', newline='\n').write(text)
    return idx


for project in PROJECTS:
    base = os.path.join(ROOT, project['dir'])
    tdir = os.path.join(base, 'entry', 'src', 'ohosTest', 'ets', 'test')
    print('==', project['short'])
    index = 1
    for fname, cases in project['files'].items():
        path = os.path.join(tdir, fname)
        index = transform_file(path, project, cases, index)
    print('   cases:', index - 1)
