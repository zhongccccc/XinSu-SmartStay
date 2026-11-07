import io
p = r'E:\zhikong\tools\write_docs.py'
raw = io.open(p, encoding='utf-8').read()
i = raw.find('README_SECTION')
print(repr(raw[i:i+120]))
