import re, sys
p = sys.argv[1]
text = open(p, encoding='utf-8').read()
old = """async function allowPermission(driver: Driver): Promise<void> {
  let allow = await driver.findComponent(ON.text('允许', MatchPattern.EQUALS));
  if (allow !== null) {
    await allow.click();
    await driver.delayMs(1000);
  }
}"""
new = """async function allowPermission(driver: Driver): Promise<void> {
  let allow = await driver.findComponent(ON.text('允许', MatchPattern.EQUALS));
  if (allow !== null) {
    await allow.click();
    await driver.delayMs(1000);
    return;
  }
  // 系统权限弹窗不在应用窗口内时，UiTest 可能无法按文本检索，使用坐标兜底点击“允许”
  await driver.click(519, 728);
  await driver.delayMs(1000);
}"""
if old not in text:
    print('pattern not found in', p)
else:
    text = text.replace(old, new)
    open(p, 'w', encoding='utf-8').write(text)
    print('patched', p)
