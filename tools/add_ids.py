import re, sys
p = sys.argv[1]
text = open(p, encoding='utf-8').read()
counter = [0]
def repl(m):
    counter[0] += 1
    indent = m.group(1)
    return "{\n" + indent + "id: " + str(counter[0]) + ",\n" + indent + "searchText:"
text = re.sub(r'\{\r?\n(\s+)searchText:', repl, text)
counter2 = [0]
def repl2(m):
    counter2[0] += 1
    return "{ id: " + str(counter2[0]) + ", searchText:"
text = re.sub(r'\{ searchText:', repl2, text)
open(p, 'w', encoding='utf-8').write(text)
print('entries patched:', counter[0] + counter2[0])
