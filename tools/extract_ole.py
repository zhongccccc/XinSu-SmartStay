import zipfile, sys, os
src = sys.argv[1]
out = sys.argv[2]
with zipfile.ZipFile(src) as z:
    data = z.read('word/embeddings/oleObject1.bin')
open(out, 'wb').write(data)
print('size', len(data), 'magic', data[:8])
