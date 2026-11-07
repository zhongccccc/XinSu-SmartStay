# -*- coding: utf-8 -*-
import io

PATH = r'D:\XTS\code\SystemFeature\Security\CertificateFramework\README_zh.md'
text = io.open(PATH, encoding='utf-8').read()

con_start = text.find('### 约束与限制')
con_end = text.find('### 下载', con_start)
assert con_start != -1 and con_end != -1
text = text[:con_start] + '''### 约束与限制

1. 本示例仅支持标准系统上运行；
2. 本示例已适配 OpenHarmony API 26.0.0 版本 SDK（`compileSdkVersion` / `compatibleSdkVersion` / `targetSdkVersion` = `26.0.0`），hvigor 版本与 `modelVersion` 已固定为 26.0.0，不再需要切换 SDK 版本的同步规避步骤；
3. 本示例需要使用 DevEco Studio（Build Version: DS-261.23567.138.36.2600851）及以上版本才可编译运行；
4. 本示例不需要申请权限，也无需替换 Full SDK。

''' + text[con_end:]

io.open(PATH, 'w', encoding='utf-8', newline='\n').write(text)

# 英文 README
PATH_EN = r'D:\XTS\code\SystemFeature\Security\CertificateFramework\README.md'
en = io.open(PATH_EN, encoding='utf-8').read()
en = en.replace(
    '2. This sample has been adapted to the API version 11 SDK, Applicable version: CI DailyBuild of 4.1.5.3 after 2023-12-23, or later Beta/Release versions.',
    '2. This sample has been adapted to OpenHarmony API 26.0.0 (compileSdkVersion / compatibleSdkVersion / targetSdkVersion = 26.0.0).')
en = en.replace(
    '3. This sample requires DevEco Studio 4.0 Release (Build Version: 4.0.0.600) or later version to compile and run. Due to the limitation of hvigor, there are some restrictions when syncing hvigor for this sample. Please follow the steps below to work around it:',
    '3. This sample requires DevEco Studio (Build Version: DS-261.23567.138.36.2600851) or later to compile and run.')
io.open(PATH_EN, 'w', encoding='utf-8', newline='\n').write(en)
print('cert readme updated')
