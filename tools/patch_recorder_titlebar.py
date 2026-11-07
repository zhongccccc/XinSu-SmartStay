import io
p = r'D:\XTS\code\SystemFeature\Media\Recorder\entry\src\main\ets\common\TitleWithBack.ets'
t = io.open(p, encoding='utf-8').read()
t = t.replace("  private title: string = '';", "  @Prop title: string = '';")
t = t.replace("          router.replaceUrl({ url: 'pages/Index' });", "          router.back();")
io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('titlebar patched')
