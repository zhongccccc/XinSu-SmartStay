import sys
p = sys.argv[1]
text = open(p, encoding='utf-8').read()
text = text.replace("""        if (publishBtn !== null) {
          await publishBtn.click();
        }
        await driver.delayMs(2000);
        await waitForText(driver, PREVIEW_TITLE_TEXT);""", """        if (publishBtn !== null) {
          await publishBtn.click();
        }
        await driver.delayMs(2000);
        // 首��发布时系统会弹出通知授权弹窗
        await allowNotification(driver);
        await driver.delayMs(1000);
        await waitForText(driver, PREVIEW_TITLE_TEXT);""")
open(p, 'w', encoding='utf-8').write(text)
print('patched')
