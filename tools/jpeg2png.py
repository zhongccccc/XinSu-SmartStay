# -*- coding: utf-8 -*-
import sys
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
Image.open(src).convert('RGB').save(dst, 'PNG')
print('converted', dst)
