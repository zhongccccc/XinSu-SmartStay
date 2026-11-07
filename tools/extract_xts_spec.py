# -*- coding: utf-8 -*-
"""提取 XTS 编码规范手册全文（段落 + 表格），输出为文本文件。"""
import io
import sys

from docx import Document

src = sys.argv[1]
dst = sys.argv[2]

doc = Document(src)
out = []


def walk_block(block):
    for p in block.paragraphs:
        text = p.text.strip()
        if text:
            style = p.style.name if p.style is not None else ''
            out.append('[{}] {}'.format(style, text))
    for t in block.tables:
        out.append('<<TABLE>>')
        for row in t.rows:
            cells = []
            for c in row.cells:
                cells.append(' '.join(x.strip() for x in c.text.splitlines() if x.strip()))
            out.append(' | '.join(cells))
        out.append('<<END TABLE>>')


# 正文
walk_block(doc)
# 页眉页脚
for section in doc.sections:
    for part in (section.header, section.footer):
        if part is not None:
            walk_block(part)

io.open(dst, 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
print('paragraphs/tables written:', len(out))
