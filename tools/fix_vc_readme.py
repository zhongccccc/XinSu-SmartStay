# -*- coding: utf-8 -*-
import io
import re

PATH = r'D:\XTS\code\SystemFeature\Media\VoiceCallDemo\README_zh.md'
text = io.open(PATH, encoding='utf-8').read()

start = text.find('### 约束与限制')
end = text.find('### 下载', start)
assert start != -1 and end != -1

new_block = '''### 约束与限制

1. 本示例仅支持标准系统上运行；
2. 本示例为 Stage 模型，已适配 OpenHarmony API 26.0.0 版本 SDK（`compileSdkVersion` / `compatibleSdkVersion` / `targetSdkVersion` = `26.0.0`）；
3. 本示例需要使用 DevEco Studio（Build Version: DS-261.23567.138.36.2600851）及以上版本才可编译运行；
4. 本示例不再使用 `setAudioScene` 等系统接口，无需替换 Full SDK；
5. 本示例仅申请 `ohos.permission.MICROPHONE`、`ohos.permission.INTERNET`、`ohos.permission.GET_WIFI_INFO`，不需要 system_basic 级别签名或 `hos_system_app` 应用类型；
6. 悬浮窗能力依赖 `ohos.permission.SYSTEM_FLOAT_WINDOW`（系统权限），普通应用无法申请，点击“切换悬浮窗”时主窗口最小化、功能自动降级，其余通话流程不受影响；
7. 完整的“聊天应用发起通话”场景需要两台设备与 `StageSocket` 示例配合，单独运行本示例时可直接在两台设备上分别进入接听页面体验。

'''
text = text[:start] + new_block + text[end:]
io.open(PATH, 'w', encoding='utf-8', newline='\n').write(text)
print('voicecall constraints updated')
