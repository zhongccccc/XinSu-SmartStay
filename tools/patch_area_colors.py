import io
p = r'D:\XTS\code\SystemFeature\WindowManagement\WindowManage\entry\src\main\ets\touchable\pages\SetTouchableAreas.ets'
t = io.open(p, encoding='utf-8').read()
for color in ('blue', 'red', 'green'):
    old = '.backgroundColor($r("app.color.%s"))' % color
    new = old + '\n        .fontColor(Color.White)'
    if '.fontColor(Color.White)' not in t.split(old)[1][:60] if old in t else True:
        pass
    t = t.replace(old, new)
io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
print(t.count('fontColor(Color.White)'))
