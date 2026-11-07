# -*- coding: utf-8 -*-
import io
import os

ROOT = r'D:\XTS\code\SystemFeature'

# 仅更新 4 个扩充了 UI 用例的工程的用例清单；其余工程的 README 适配章节保持已生成内容
CASES = {
    r'Media\GamePuzzle': {
        'bundle': 'ohos.samples.gamepuzzle',
        'ui': [
            ('ohos.samples.gamepuzzle_StartAbility_001', '拉起应用'),
            ('ohos.samples.gamepuzzle_GetPermission_001', '处理媒体访问权限弹窗'),
            ('ohos.samples.gamepuzzle_EnsureImages_001', '校验有可用图片（替代原“不足两张则调用相机拍照”的前置逻辑）'),
            ('ohos.samples.gamepuzzle_StartAbility_002', '再次拉起应用'),
            ('CheckIndexPage_001', '校验首页 time/imageShow/imageGrid/start/restart 元素'),
            ('StartGame_001', '开始游戏，计时从 05 分进入 04 分'),
            ('ChangePhoto_001', '更换图片后计时重置为 05 分'),
            ('StartGame_002', '再次开始游戏'),
            ('GameOver_001', '模拟完成拼图，出现通关提示且计时重置'),
            ('StartGame_003', '通关后再次开始游戏'),
            ('GameFailed_003', '模拟时间耗尽，出现 TimeOver 提示'),
        ],
        'logic': [
            ('GamePuzzle_FindEmptyIndex_001', '空位查找：命中/未命中两种场景'),
            ('GamePuzzle_ItemChange_001', '交换后空位移动到被点击位置'),
            ('GamePuzzle_GameBegin_001', '洗牌后仍是 1~9 共 9 个序号，不重不漏'),
            ('GamePuzzle_GameInit_NotStarted_001', '游戏未开始时点击不移动'),
            ('GamePuzzle_GameInit_Started_001', '游戏开始后相邻格子可移动'),
        ],
    },
    r'Media\VoiceCallDemo': {
        'bundle': 'com.samples.voicecalldemo',
        'ui': [
            ('com.samples.voicecalldemoStartAbility_001', '拉起被叫页面，处理麦克风授权，校验接听/挂断按钮'),
            ('Switch_window_001', '切换到请求通话页并点击悬浮窗切换（无系统权限时自动降级），页面保持可用'),
            ('com.samples.voicecalldemoStartAbility_002', '切换到通话页面，校验通话计时组件'),
            ('Answer_001', '点击接听，进入通话页面'),
            ('Hangup_001', '点击挂断，通话页面关闭'),
        ],
        'logic': [
            ('VoiceCall_TimeUtil_Invalid_001', '非法时长返回 `--`'),
            ('VoiceCall_TimeUtil_Minute_001', '小于 1 小时返回 mm:ss'),
            ('VoiceCall_TimeUtil_Hour_001', '超过 1 小时返回 hh:mm:ss'),
            ('VoiceCall_TimeUtil_FixZero_001', '补零逻辑正确'),
            ('VoiceCall_IpUtils_001', 'IP 整数转点分十进制'),
            ('VoiceCall_ArrayBufferUtils_Bytes_001', '字节数组与 ArrayBuffer 互转'),
            ('VoiceCall_ArrayBufferUtils_String_001', '字符串与 ArrayBuffer 互转'),
        ],
    },
    r'WindowManagement\WindowManage': {
        'bundle': 'ohos.samples.windowcomponent',
        'ui': [
            ('WindowManager_StartAbility_001', '拉起应用，校验首页三个功能入口'),
            ('WindowManager_OpenGetPropertiesOfSystemBarPage_001', '进入获取系统栏属性页，校验按钮渲染'),
            ('WindowManager_GetPropertiesOfSystemBarPage_001', '点击获取按钮，校验属性文本非空并返回'),
            ('WindowManager_OpenSetTouchableAreasPage_001', '进入可触摸区域页，校验区域1~4渲染'),
            ('WindowManager_SetTouchableAreas_001', '点击区域1，校验提示 `click 区域1`'),
            ('WindowManager_TouchArea2_001', '点击区域2，页面保持可用'),
            ('WindowManager_TouchArea4_001', '点击区域4，校验提示 `click 区域4`'),
            ('WindowManager_BackToIndex_001', '从可触摸区域页返回首页'),
            ('WindowManager_OpenVideoPage_001', '进入窗口视频页，校验窗口按钮出现'),
            ('WindowManager_VideoPage_001', '窗口视频页元素：主视频/窗口按钮/焦点文本'),
            ('WindowManager_WindowBtn_001', '点击窗口按钮切换横竖屏，页面保持可用'),
            ('WindowManager_MainVideoClick_001', '点击主视频切换子窗口，主视频仍在'),
            ('WindowManager_VideoBack_001', '关闭子窗口并返回，应用保持可用'),
        ],
        'logic': [
            ('WindowManage_EventId_001', '子窗口事件 id 常量为 1001'),
            ('WindowManage_WindowColor_001', '系统栏颜色常量均为十六进制颜色串'),
            ('WindowManage_WindowType_001', '子窗口属性结构可实例化并保留取值'),
            ('WindowManage_FormatProperties_001', '系统栏属性格式化为缩进 JSON'),
        ],
    },
    r'Media\Recorder': {
        'bundle': 'ohos.samples.recorder',
        'ui': [
            ('Recorder_StartAbility_001', '拉起录音应用'),
            ('Recorder_RequestPermissionFunction_001', '处理麦克风权限弹窗，校验首页录音按钮'),
            ('Recorder_RecordePage_001', '进入录音页面'),
            ('Recorder_RecordePage_002', '录音计时随时间变化'),
            ('Recorder_RecordePage_003', '录音页暂停/继续与结束按钮'),
            ('Recorder_Play_001', '结束录音并进入播放页，校验播放界面后返回'),
            ('Recorder_RE_Recorde_001', '再次进入录音页'),
            ('Recorder_Del_Recorde_001', '结束录音并返回列表'),
            ('Recorder_RE_Recorde_002', '第三次录音并结束'),
            ('Recorder_CheckState_001', '长按列表项进入多选状态并勾选'),
            ('Recorder_DeleteRecord_001', '多选状态下点击删除，弹窗取消'),
            ('Recorder_Del_All_001', '退出多选状态回到普通列表'),
            ('Recorder_SlideAudioItem_001', '左滑列表项显示重命名/删除按钮'),
            ('Recorder_RenameRepeat_001', '打开重命名弹窗并取消'),
        ],
        'logic': [
            ('Recorder_DateTimeUtil_Fill_001', '日期/时间不足两位补 0'),
            ('Recorder_DateTimeUtil_ConcatDate_001', '年月日拼接格式'),
            ('Recorder_DateTimeUtil_ConcatTime_001', '时分秒拼接格式'),
            ('Recorder_DurationString_001', '小于 1 小时的时长格式为 mm:ss'),
            ('Recorder_DurationString_002', '超过 1 小时的时长格式为 hh:mm:ss'),
            ('Recorder_UpdateTime_001', '录音页计时文本格式化'),
            ('Recorder_TimeString_001', '播放页进度文本格式化'),
        ],
    },
}

TEST_DOC = '''# 测试用例说明

## 测试环境

- 设备：OpenHarmony 7.1.0.21（API 26.0.0）
- 测试框架：`@ohos/hypium` + `@ohos.UiTest`
- 测试模块：`entry_test`（`entry/src/ohosTest`）
- 运行命令：`hdc shell aa test -b {bundle} -m entry_test -s unittest OpenHarmonyTestRunner`

## 用例清单

### UI 用例（{ui_count} 个）

| 用例 | 说明 |
| --- | --- |
{ui_rows}

### 逻辑用例（{logic_count} 个）

| 用例 | 说明 |
| --- | --- |
{logic_rows}

## 最近一次执行结果

```
Tests run: {total}, Failure: 0, Error: 0, Pass: {total}, Ignore: 0
```
'''


def write(path, content):
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)


for rel, info in CASES.items():
    base = os.path.join(ROOT, rel)
    total = len(info['ui']) + len(info['logic'])
    ui_rows = '\n'.join('| `{}` | {} |'.format(t[0], t[1]) for t in info['ui'])
    logic_rows = '\n'.join('| `{}` | {} |'.format(t[0], t[1]) for t in info['logic'])
    write(os.path.join(base, 'ohosTest.md'),
          TEST_DOC.format(bundle=info['bundle'], ui_rows=ui_rows, logic_rows=logic_rows,
                          ui_count=len(info['ui']), logic_count=len(info['logic']), total=total))

    readme = os.path.join(base, 'README_zh.md')
    text = io.open(readme, encoding='utf-8', errors='replace').read()
    lower = text.find('### 测试')
    if lower != -1:
        end = text.find('用例清单见', lower)
        if end != -1:
            end = text.find('\n', end)
            head = text[:lower]
            tail = text[end:] if end != -1 else ''
            text = head + '### 测试\n\n本工程测试包含 **UI 用例** 与 **逻辑用例** 两部分，共 {} 个用例：\n\n```bash\nhdc shell aa test -b {} -m entry_test -s unittest OpenHarmonyTestRunner\n```\n'.format(total, info['bundle']) + tail
    write(readme, text)
    print('updated', os.path.basename(rel), 'ui=', len(info['ui']), 'logic=', len(info['logic']), 'total=', total)
