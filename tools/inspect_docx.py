# -*- coding: utf-8 -*-
"""列出 docx 包内的媒体/嵌入文件，并统计 document.xml 中的文本框与图片数量。"""
import io
import os
import re
import sys
import zipfile

src = sys.argv[1]
outdir = sys.argv[2]
os.makedirs(outdir, exist_ok=True)

with zipfile.ZipFile(src) as z:
    names = z.namelist()
    media = [n for n in names if n.startswith('word/media/')]
    embeds = [n for n in names if 'embed' in n.lower() or n.endswith('.bin') or n.endswith('.docx') or n.endswith('.ets')]
    print('total parts:', len(names))
    print('media files:', len(media))
    for n in media:
        info = z.getinfo(n)
        print('  {} {} bytes'.format(n, info.file_size))
    print('embed files:', embeds)

    xml = z.read('word/document.xml').decode('utf-8', errors='replace')
    print('textboxes:', len(re.findall(r'w:txbxContent', xml)))
    print('drawings:', len(re.findall(r'<w:drawing', xml)))
    print('tables:', len(re.findall(r'<w:tbl>', xml)))
    print('sectPr:', len(re.findall(r'<w:sectPr', xml)))

    # 导出媒体
    for n in media:
        base = os.path.basename(n)
        with open(os.path.join(outdir, base), 'wb') as f:
            f.write(z.read(n))
