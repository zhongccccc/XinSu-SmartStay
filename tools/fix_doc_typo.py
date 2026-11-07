import io
p = r'E:\zhikong\tools\update_docs_xts.py'
t = io.open(p, encoding='utf-8').read()
t = t.replace('`@ohos.hypium`', '`@ohos/hypium`')
io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('fixed')
