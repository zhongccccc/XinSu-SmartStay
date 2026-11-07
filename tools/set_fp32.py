import re
p = '/opt/zhikong/face/config.yaml'
s = open(p, encoding='utf-8').read()
s = s.replace('arcface: models/arcface_mobilefacenet_cut.q.onnx',
              'arcface: models/arcface_mobilefacenet_cut.onnx')
open(p, 'w', encoding='utf-8').write(s)
for line in s.splitlines():
    if 'arcface:' in line or 'num_threads' in line or 'detector:' in line:
        print(line)
