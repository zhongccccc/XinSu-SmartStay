import sys
p = sys.argv[1]
text = open(p, encoding='utf-8').read()
text = text.replace("""        await driver.delayMs(2500);
        await waitForText(driver, PAGE_TITLE_TEXT);""", """        await driver.delayMs(2500);
        await allowNotification(driver);
        await waitForText(driver, PAGE_TITLE_TEXT);""")
text = text.replace("""        let driver = Driver.create();
        await driver.delayMs(1000);
        let publishBtn""", """        let driver = Driver.create();
        await driver.delayMs(1000);
        await allowNotification(driver);
        let publishBtn""")
text = text.replace("""/**
 * 等待指定文本组件出现
 */""", """/**
 * 处理通知权限弹窗
 */
async function allowNotification(driver: Driver): Promise<void> {
  let allow = await driver.findComponent(ON.text('允许', MatchPattern.EQUALS));
  if (allow !== null) {
    await allow.click();
    await driver.delayMs(1000);
    return;
  }
  // 系统弹窗不在应用窗口内时按坐标兜底点击“允许”
  await driver.click(504, 743);
  await driver.delayMs(1000);
}

/**
 * 等待指定文本组件出现
 */""")
open(p, 'w', encoding='utf-8').write(text)
print('patched')
