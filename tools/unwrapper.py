import sys
p = sys.argv[1]
text = open(p, encoding='utf-8').read()
text = text.replace("    beforeAll(async () => {\n", "", 1)
open(p, 'w', encoding='utf-8').write(text)
print('removed wrapper')
