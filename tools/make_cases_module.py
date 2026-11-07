# -*- coding: utf-8 -*-
import io
import re

src = r'E:\zhikong\tools\xts_normalize_tests.py'
text = io.open(src, encoding='utf-8').read()
start = text.index('PROJECTS = [')
end = text.index('\n]\n', start) + 3
data = text[start:end]
io.open(r'E:\zhikong\tools\xts_cases.py', 'w', encoding='utf-8', newline='\n').write(
    '# -*- coding: utf-8 -*-\n' + data + '\n')
print('xts_cases.py written, chars:', len(data))
