import io
p = r'E:\zhikong\tools\xts_normalize_tests2.py'
t = io.open(p, encoding='utf-8').read()
t = t.replace("        if old_comment and '@tc.' not in old_comment.group(0):\n            before = before[:old_comment.start()]\n", "        if old_comment and '@tc.' not in old_comment.group(0):\n            before = before[:old_comment.start()].rstrip(' \\t')\n")
io.open(p, 'w', encoding='utf-8', newline='\n').write(t)

c = r'E:\zhikong\tools\xts_cases.py'
s = io.open(c, encoding='utf-8').read()
s = s.replace("('com.samples.notificationpublish_PublishNotification_001', 'PublishNotification',", "('com.samples.notificationpublish_PublishNotification_001', 'Notification',")
io.open(c, 'w', encoding='utf-8', newline='\n').write(s)
print('patched')
