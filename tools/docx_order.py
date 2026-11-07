# -*- coding: utf-8 -*-
"""按文档顺序输出段落文本与内嵌图片文件名（写入文件，避免控制台编码问题）。"""
import io
import re
import sys
import zipfile

from docx import Document
from docx.oxml.ns import qn

src = sys.argv[1]
dst = sys.argv[2]

with zipfile.ZipFile(src) as z:
    rels_xml = z.read('word/_rels/document.xml.rels').decode('utf-8')
rels = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', rels_xml))
for target, rid in re.findall(r'Target="([^"]+)"[^>]*Id="([^"]+)"', rels_xml):
    rels.setdefault(rid, target)

doc = Document(src)
body = doc.element.body
lines = []
idx = 0
for child in body.iterchildren():
    if child.tag == qn('w:p'):
        texts = [n.text for n in child.iter(qn('w:t')) if n.text]
        text = ''.join(texts).strip()
        embeds = []
        for blip in child.iter(qn('a:blip')):
            rid = blip.get(qn('r:embed'))
            if rid and rid in rels:
                embeds.append(rels[rid].split('/')[-1])
        if text or embeds:
            idx += 1
            lines.append('{:03d} P: {}{}'.format(
                idx, text, ('   [IMG ' + ','.join(embeds) + ']') if embeds else ''))
    elif child.tag == qn('w:tbl'):
        idx += 1
        lines.append('{:03d} TABLE'.format(idx))

io.open(dst, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print('lines:', len(lines))
