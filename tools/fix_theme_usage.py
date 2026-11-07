# -*- coding: utf-8 -*-
import io

PATH = r'D:\XTS\code\SystemFeature\ResourceAllocation\ApplicationThemeSwitch\README_zh.md'
text = io.open(PATH, encoding='utf-8').read()
old = '2. 系统深浅模式切换，应用主题自动跟随切换深浅模式。'
new = ('2. 选择“白天/夜晚”时，应用通过 `ApplicationContext.setColorMode` 切换深浅色，对应 `light`/`dark` 资源目录生效；'
       '选择“自定义”时使用自定义配色资源。')
if old in text:
    text = text.replace(old, new)
    io.open(PATH, 'w', encoding='utf-8', newline='\n').write(text)
    print('themeswitch usage updated')
else:
    print('pattern not found')
