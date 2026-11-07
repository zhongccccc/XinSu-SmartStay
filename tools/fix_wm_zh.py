import sys
p = sys.argv[1]
text = open(p, encoding='utf-8').read()
mapping = {
    "'window video'": "'窗口视频'",
    "'set touchable area of window page'": "'设置窗口可触摸区域页'",
    "'get properties of system bar page'": "'获取系统状态栏属性页'",
    "'get properties of system bar'": "'获取系统栏属性'",
    "'area1'": "'区域1'",
    "'area2'": "'区域2'",
    "'area3'": "'区域3'",
    "'area4'": "'区域4'",
}
for k, v in mapping.items():
    text = text.replace(k, v)
open(p, 'w', encoding='utf-8').write(text)
print('done')
