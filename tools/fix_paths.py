# -*- coding: utf-8 -*-
import io

fixes = [
    (r'D:\XTS\code\SystemFeature\Notification\Publish\README_zh.md',
     [('`model/NotificationModel.ets`', '`entry/src/main/ets/model/NotificationModel.ets`')]),
    (r'D:\XTS\code\SystemFeature\WindowManagement\WindowManage\README_zh.md',
     [('`utils/WindowFormat.ets`', '`entry/src/main/ets/utils/WindowFormat.ets`')]),
    (r'D:\XTS\code\SystemFeature\Security\CertificateFramework\README_zh.md',
     [('`testrunner/OpenHarmonyTestRunner.ts`', '`entry/src/ohosTest/ets/testrunner/OpenHarmonyTestRunner.ts`')]),
    (r'D:\XTS\code\SystemFeature\Security\CertificateFramework\README.md',
     [('`testrunner/OpenHarmonyTestRunner.ts`', '`entry/src/ohosTest/ets/testrunner/OpenHarmonyTestRunner.ts`')]),
]

for path, pairs in fixes:
    text = io.open(path, encoding='utf-8').read()
    for old, new in pairs:
        if old in text:
            text = text.replace(old, new)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(text)
    print('fixed', path.split('\\')[-2], path.split('\\')[-1])
