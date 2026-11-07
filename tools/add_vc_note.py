# -*- coding: utf-8 -*-
import io

PATH = r'D:\XTS\code\SystemFeature\Media\VoiceCallDemo\README_zh.md'
text = io.open(PATH, encoding='utf-8').read()
anchor = '| ![image](screenshots/devices/ring_up.jpeg) | ![image](screenshots/devices/incoming.jpeg) | ![image](screenshots/devices/voice.jpeg) | ![image](screenshots/devices/float_win.jpeg) |'
note = ('\n\n> 说明：悬浮窗截图用于展示开启系统权限后的效果；普通应用无法申请 `ohos.permission.SYSTEM_FLOAT_WINDOW`，'
        '点击“切换悬浮窗”时主窗口最小化（功能降级），其余通话流程正常。')
if '悬浮窗截图' not in text:
    assert anchor in text
    text = text.replace(anchor, anchor + note, 1)
    io.open(PATH, 'w', encoding='utf-8', newline='\n').write(text)
    print('note added')
else:
    print('note exists')
