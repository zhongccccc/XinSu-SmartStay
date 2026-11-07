import io
p = r'D:\XTS\code\SystemFeature\Media\Recorder\entry\src\main\ets\common\PlayView.ets'
t = io.open(p, encoding='utf-8').read()
t = t.replace("  private duration: string = '';", "  @Prop duration: string = '';")
io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('playview patched')
