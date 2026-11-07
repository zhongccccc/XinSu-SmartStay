import io
for p in [r'D:\XTS\code\SystemFeature\Media\Recorder\entry\src\ohosTest\ets\test\Ability.test.ets',
          r'D:\XTS\code\SystemFeature\Media\VoiceCallDemo\entry\src\ohosTest\ets\test\App.test.ets']:
    raw = io.open(p, encoding='utf-8').read()
    i = raw.find("'允许'")
    print(p.split('\\')[-1], 'found 允许:', i != -1, repr(raw[i:i+12]) if i!=-1 else '')
