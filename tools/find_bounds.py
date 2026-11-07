import json,sys
p = sys.argv[1]
raw = open(p, encoding='utf-8').read()
# 文件是 JSON + 可能前缀文本，尝试截取第一个 {
start = raw.find('{')
data = json.loads(raw[start:])
def walk(node, depth=0):
    attrs = node.get('attributes', {})
    text = attrs.get('text', '')
    if text in ('允许', '不允许'):
        print(text, attrs.get('bounds'))
    for c in node.get('children', []):
        walk(c, depth+1)
walk(data)
