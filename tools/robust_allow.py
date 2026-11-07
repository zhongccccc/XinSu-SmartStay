# -*- coding: utf-8 -*-
import io
import re

FILES = [
    r'D:\XTS\code\SystemFeature\Notification\Publish\entry\src\ohosTest\ets\test\Ability.test.ets',
    r'D:\XTS\code\SystemFeature\Media\GamePuzzle\entry\src\ohosTest\ets\test\Ability.test.ets',
    r'D:\XTS\code\SystemFeature\Media\VoiceCallDemo\entry\src\ohosTest\ets\test\App.test.ets',
    r'D:\XTS\code\SystemFeature\Media\Recorder\entry\src\ohosTest\ets\test\Ability.test.ets',
]

HELPER = '''/**
 * 计算权限弹窗“允许”按钮的屏幕相对位置（适配不同分辨率）
 */
function allowButtonPoint(): number[] {
  let info = display.getDefaultDisplaySync();
  let x = Math.floor(info.width * 0.71);
  let y = Math.floor(info.height * 0.575);
  return [x, y];
}
'''

for path in FILES:
    text = io.open(path, encoding='utf-8').read()
    # 1) 注入 display 导入
    if "from '@kit.ArkUI'" not in text:
        if "import { hilog } from '@kit.PerformanceAnalysisKit';" in text:
            text = text.replace("import { hilog } from '@kit.PerformanceAnalysisKit';",
                                "import { hilog } from '@kit.PerformanceAnalysisKit';\nimport { display } from '@kit.ArkUI';", 1)
        else:
            m = re.search(r"^(import .+;)$", text, re.M)
            if m:
                text = text[:m.end()] + "\nimport { display } from '@kit.ArkUI';" + text[m.end():]
    # 2) 替换固定坐标点击
    text = text.replace("await driver.click(519, 728);", "let point = allowButtonPoint();\n  await driver.click(point[0], point[1]);")
    text = text.replace("await driver.click(504, 743);", "let point = allowButtonPoint();\n  await driver.click(point[0], point[1]);")
    # 3) 注入辅助函数（若不存在）
    if 'allowButtonPoint' in text and 'function allowButtonPoint' not in text:
        anchor = text.rfind('/**')
        text = text + "\n" + HELPER
    io.open(path, 'w', encoding='utf-8', newline='\n').write(text)
    print('patched', path.split('\\')[-1], 'points:', text.count('allowButtonPoint()'))
