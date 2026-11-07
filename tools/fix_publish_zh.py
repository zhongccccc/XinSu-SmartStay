import sys
p = sys.argv[1]
text = open(p, encoding='utf-8').read()
text = text.replace("const PAGE_TITLE_TEXT = 'notification';", "const PAGE_TITLE_TEXT = '实况通知';")
text = text.replace("const PUBLISH_BUTTON_TEXT = 'pubNot';", "const PUBLISH_BUTTON_TEXT = '发布通知';")
text = text.replace("const PREVIEW_TITLE_TEXT = 'title';", "const PREVIEW_TITLE_TEXT = '通知标题';")
open(p, 'w', encoding='utf-8').write(text)
print('ok')
