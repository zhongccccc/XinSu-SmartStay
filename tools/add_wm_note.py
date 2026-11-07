# -*- coding: utf-8 -*-
import io

PATH = r'D:\XTS\code\SystemFeature\WindowManagement\WindowManage\README_zh.md'
text = io.open(PATH, encoding='utf-8').read()
anchor = '| <img src="screenshots/devices/setTouchableAreas.jpg" width="400"> | <img src="screenshots/devices/getPropertiesOfSystemBar.jpg" width="400">    |'
note = ('\n\n> 说明：上表中“拉起悬浮应用”截图对应已安装 `WindowRatio` 示例（`com.samples.windowratio`）时的效果；'
        '未安装时点击该按钮仅提示启动失败，不影响本示例其他页面。')
if 'WindowRatio' in text and '拉起悬浮应用”截图' not in text:
    assert anchor in text
    text = text.replace(anchor, anchor + note, 1)
    io.open(PATH, 'w', encoding='utf-8', newline='\n').write(text)
    print('note added')
else:
    print('skip')
