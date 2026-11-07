# -*- coding: utf-8 -*-
"""WindowManage 小问题修复：
1) 子窗口打开时按返回无效（子窗口吞掉返回事件）→ 子窗口返回先关闭自身；
2) 子窗口页面“拉起悬浮应用”失败无任何提示 → 增加 toast；
3) 视频页初始显示 “unknown” 调试文案 → 初始为空，仅事件后显示；
4) 可触摸区域页 area2/3/4 深色文字在彩色背景上对比度低 → 改白字。
"""
import io
import json
import os
import re

ROOT = r'D:\XTS\code\SystemFeature\WindowManagement\WindowManage'

# ---------- 1. WindowConst 增加关闭子窗口事件 ----------
p = os.path.join(ROOT, r'WindowComponent\src\main\ets\components\util\WindowConst.ts')
t = io.open(p, encoding='utf-8').read()
if 'SUB_WINDOW_CLOSE_EVENT_ID' not in t:
    t = t.replace("export const WindowEventId = {\n  SUB_WINDOW_INNER_EVENT_ID: 1001,\n}",
                  "export const WindowEventId = {\n  SUB_WINDOW_INNER_EVENT_ID: 1001,\n"
                  "  SUB_WINDOW_CLOSE_EVENT_ID: 1002,\n}")
    io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
    print('WindowConst updated')

# ---------- 2. MainPage：关闭子窗口能力 / 初始文案 ----------
p = os.path.join(ROOT, r'WindowComponent\src\main\ets\components\MainPage\MainPage.ets')
t = io.open(p, encoding='utf-8').read()

t = t.replace(
    "import window from '@ohos.window';",
    "import window from '@ohos.window';\nimport emitter from '@ohos.events.emitter';")

t = t.replace(
    "  @StorageLink('focusText') focusText: string = 'unknown';",
    "  @StorageLink('focusText') focusText: string = '';")

# 插入 closeSubWindow 方法
anchor = """  aboutToAppear() {
    this.context = getContext(this) as common.UIAbilityContext;"""
if 'async closeSubWindow()' not in t:
    t = t.replace(anchor, """  async closeSubWindow() {
    if (!this.showSubWindow) {
      return;
    }
    try {
      let windows = await this.subWindow?.getSubWindow();
      if (windows !== undefined && windows.length > 0) {
        await windows[0].destroyWindow();
      }
    } catch (err) {
      console.error('destroy sub window failed: ' + JSON.stringify(err));
    }
    this.showSubWindow = false;
    WindowManger.destorySubWindowCallback();
    this.videoController.start();
  }

  aboutToAppear() {
    AppStorage.SetOrCreate('focusText', '');
    emitter.on({
      eventId: WindowEventId.SUB_WINDOW_CLOSE_EVENT_ID,
      priority: emitter.EventPriority.HIGH
    }, () => {
      this.closeSubWindow();
    });
    this.context = getContext(this) as common.UIAbilityContext;""")

# aboutToDisappear：关闭子窗口并注销监听
if 'aboutToDisappear()' not in t:
    t = t.replace("""  build() {
    Column() {
      Column() {
        Video({""", """  aboutToDisappear() {
    emitter.off(WindowEventId.SUB_WINDOW_CLOSE_EVENT_ID);
    this.closeSubWindow();
  }

  build() {
    Column() {
      Column() {
        Video({""")

# 复用 closeSubWindow
t = t.replace("""            if (this.showSubWindow) {
              this.videoController.start();
              let windows = await this.subWindow?.getSubWindow();
              if (windows !== undefined) {
                windows[0].destroyWindow();
                this.showSubWindow = false;
                WindowManger.destorySubWindowCallback();
              }
            } else {""", """            if (this.showSubWindow) {
              await this.closeSubWindow();
            } else {""")

io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('MainPage updated')

# ---------- 3. SubWindowPage：返回关闭子窗口 + 拉起失败提示 ----------
p = os.path.join(ROOT, r'entry\src\main\ets\pages\SubWindowPage.ets')
t = io.open(p, encoding='utf-8').read()

t = t.replace("import Want from '@ohos.app.ability.Want';",
              "import Want from '@ohos.app.ability.Want';\nimport promptAction from '@ohos.promptAction';")

t = t.replace("  SUB_WINDOW_INNER_EVENT_ID: number = 1001;",
              "  SUB_WINDOW_INNER_EVENT_ID: number = 1001;\n"
              "  // 与 WindowComponent 中 WindowEventId.SUB_WINDOW_CLOSE_EVENT_ID 保持一致\n"
              "  SUB_WINDOW_CLOSE_EVENT_ID: number = 1002;")

t = t.replace("""        .catch((error: BusinessError) => {
          console.log('startAbility failed, error.code: ' + JSON.stringify(error.code) +
            ' error.message: ' + JSON.stringify(error.message));
        });""", """        .catch((error: BusinessError) => {
          console.log('startAbility failed, error.code: ' + JSON.stringify(error.code) +
            ' error.message: ' + JSON.stringify(error.message));
          this.showStartFailed();
        });""")

t = t.replace("""    } catch (paramError) {
      console.log('error.code: ' + JSON.stringify(paramError.code) +
        ' error.message: ' + JSON.stringify(paramError.message));
    }
  }""", """    } catch (paramError) {
      console.log('error.code: ' + JSON.stringify(paramError.code) +
        ' error.message: ' + JSON.stringify(paramError.message));
      this.showStartFailed();
    }
  }

  showStartFailed(): void {
    promptAction.showToast({
      message: $r('app.string.start_new_ability_failed'),
      duration: 2000
    });
  }

  /**
   * 子窗口内按返回时先关闭子窗口（通过事件通知主窗口销毁），再按一次返回退出视频页
   */
  onBackPress(): boolean {
    let innerEvent: emitter.InnerEvent = {
      eventId: this.SUB_WINDOW_CLOSE_EVENT_ID,
      priority: emitter.EventPriority.HIGH
    };
    emitter.emit(innerEvent);
    return true;
  }""")

io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('SubWindowPage updated')

# ---------- 4. 可触摸区域文字颜色 ----------
p = os.path.join(ROOT, r'entry\src\main\ets\touchable\pages\SetTouchableAreas.ets')
t = io.open(p, encoding='utf-8').read()
for area in ('area2', 'area3', 'area4'):
    t = t.replace(
        "        .backgroundColor($r(\"app.color.%s\"))\n        .textAlign(TextAlign.Center)" % area,
        "        .backgroundColor($r(\"app.color.%s\"))\n        .fontColor(Color.White)\n"
        "        .textAlign(TextAlign.Center)" % area)
io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('SetTouchableAreas updated')

# ---------- 5. 字符串资源 ----------
for lang, value in (('base', 'WindowRatio sample app is not installed.'),
                    ('en', 'WindowRatio sample app is not installed.'),
                    ('zh', '未安装 WindowRatio 示例应用，无法拉起悬浮应用')):
    path = os.path.join(ROOT, r'entry\src\main\resources\%s\element\string.json' % lang)
    data = json.load(io.open(path, encoding='utf-8-sig'))
    names = [item['name'] for item in data['string']]
    if 'start_new_ability_failed' not in names:
        data['string'].append({'name': 'start_new_ability_failed', 'value': value})
        io.open(path, 'w', encoding='utf-8', newline='\n').write(
            json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        print('string added:', lang)
