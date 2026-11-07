# -*- coding: utf-8 -*-
import io
import re

FILES = [
    r'D:\XTS\code\SystemFeature\Media\GamePuzzle\entry\src\ohosTest\ets\test\Ability.test.ets',
    r'D:\XTS\code\SystemFeature\Media\VoiceCallDemo\entry\src\ohosTest\ets\test\App.test.ets',
]

BODY = '''async function allowPermission(driver: Driver): Promise<void> {
  let allow = await driver.findComponent(ON.text('允许', MatchPattern.EQUALS));
  if (allow !== null) {
    await allow.click();
    await driver.delayMs(1000);
    return;
  }
  // 系统权限弹窗不在应用窗口内时，UiTest 可能无法按文本检索，按屏幕比例兜底点击“允许”
  let point = allowButtonPoint();
  await driver.click(point[0], point[1]);
  await driver.delayMs(1000);
}

/**
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
    new_text, count = re.subn(r'async function allowPermission\(driver: Driver\): Promise<void> \{[\s\S]*?\n\}\n', BODY, text, count=1)
    if count == 0:
        print('NOT FOUND:', path)
        continue
    io.open(path, 'w', encoding='utf-8', newline='\n').write(new_text)
    print('patched', path.split('\\')[-1])
