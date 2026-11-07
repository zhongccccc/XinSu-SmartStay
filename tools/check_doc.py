import io
p = r'D:\XTS\code\SystemFeature\Media\Recorder\ohosTest.md'
text = io.open(p, encoding='utf-8').read()
print(repr(text[:60]))
print(text[:200])
