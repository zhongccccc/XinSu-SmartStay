# -*- coding: utf-8 -*-
import io

PATH = r'D:\XTS\code\SystemFeature\Media\VoiceCallDemo\README_zh.md'
text = io.open(PATH, encoding='utf-8').read()
text = text.replace(
    '普通应用无法申请 `ohos.permission.SYSTEM_FLOAT_WINDOW`，点击“切换悬浮窗”时主窗口最小化（功能降级），其余通话流程正常。',
    '普通应用未申请 `ohos.permission.SYSTEM_FLOAT_WINDOW`（系统权限），点击“切换悬浮窗”时主窗口最小化（功能降级），其余通话流程正常。')
text = text.replace(
    '- 移除 `ohos.permission.MANAGE_AUDIO_CONFIG`、`ohos.permission.SYSTEM_FLOAT_WINDOW` 等系统权限，避免普通安装失败；悬浮窗能力在无该权限时自动降级。',
    '- 移除 `ohos.permission.MANAGE_AUDIO_CONFIG`、`ohos.permission.SYSTEM_FLOAT_WINDOW` 等系统权限（未申请），避免普通安装失败；悬浮窗能力在无该权限时自动降级。')
io.open(PATH, 'w', encoding='utf-8', newline='\n').write(text)
print('voicecall wording updated')
