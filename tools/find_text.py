# -*- coding: utf-8 -*-
import json
import sys

path = sys.argv[1]
target = sys.argv[2]
raw = open(path, encoding='utf-8').read()
data = json.loads(raw[raw.find('{'):])

found = []


def walk(node):
    attrs = node.get('attributes', {})
    if attrs.get('text') == target or attrs.get('id') == target:
        found.append(attrs.get('bounds'))
    for c in node.get('children', []):
        walk(c)


walk(data)
print(found[0] if found else '')
