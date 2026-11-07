import io
p = r'D:\XTS\code\SystemFeature\Media\VoiceCallDemo\entry\src\ohosTest\ets\test\VoiceCallLogic.test.ets'
t = io.open(p, encoding='utf-8').read()
t = t.replace("import TimeUtil from '../../../main/ets/utils/TimeUtil';", "import timeUtil from '../../../main/ets/utils/TimeUtil';")
t = t.replace("import IpUtils from '../../../main/ets/utils/IpUtils';", "import ipUtils from '../../../main/ets/utils/IpUtils';")
t = t.replace("const timeUtil: TimeUtil = new TimeUtil();\n", "")
t = t.replace("const ipUtils: IpUtils = new IpUtils();\n", "")
io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('patched')
