import json, sys
p = sys.argv[1]
raw = open(p, encoding='utf-8').read()
data = json.loads(raw[raw.find('{'):])
target = sys.argv[2]
def walk(node):
    attrs = node.get('attributes', {})
    if attrs.get('id') == target:
        print(attrs.get('bounds'))
    for c in node.get('children', []):
        walk(c)
walk(data)
