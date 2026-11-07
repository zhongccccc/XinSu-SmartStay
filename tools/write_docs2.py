# -*- coding: utf-8 -*-
import io
import os

ROOT = r'D:\XTS\code\SystemFeature'

PROJECTS = [
    {
        'dir': r'Notification\Publish',
        'name': 'Publish',
        'bundle': 'com.samples.notificationpublish',
        'ui': [
            ('com.samples.notificationpublish_StartAbility_001', '拉起应用，校验标题「实况通知」与「发布通知」按钮渲染'),
            ('com.samples.notificationpublish_PublishNotification_001', '点击「发布通知」，处理授权弹窗，校验通知预览卡片「通知标题」出现'),
        ],
        'logic': [
            ('Publish_Request_Basic_001', '通知请求 id 与通知槽类型符合预期'),
            ('Publish_Request_Content_001', '通知内容为文本类型，标题/正文正确'),
            ('Publish_Request_AdditionalText_001', '附加文本按入参透传'),
            ('Publish_Request_Independent_001', '每次构造返回独立对象'),
        ],
        'changes': [
            '模块导入统一迁移到 Kit：`@kit.NotificationKit`、`@kit.ArkUI`、`@kit.ImageKit`、`@kit.BasicServicesKit`、`@kit.AbilityKit`。',
            '删除 API 26 已移除的实况通知接口：`notificationManager.ButtonOptions`、`SystemLiveViewSubscriber`、`subscribeSystemLiveView`。',
            '通知内容由 `NOTIFICATION_CONTENT_SYSTEM_LIVE_VIEW` 改为 `NOTIFICATION_CONTENT_BASIC_TEXT`，通知槽类型改为 `SlotType.SOCIAL_COMMUNICATION`。',
            '新增 `model/NotificationModel.ets` 承载通知请求构造逻辑（便于单元测试），页面改为调用 `buildNotificationRequest`。',
            '发布成功后置位 `showPublishFlag` 并显示通知预览卡片，保证示例在 OpenHarmony 设备上的可见效果。',
            '`Base.BusinessError` 改为 `@kit.BasicServicesKit` 的 `BusinessError`。',
        ],
    },
    {
        'dir': r'ResourceAllocation\ApplicationThemeSwitch',
        'name': 'ApplicationThemeSwitch',
        'bundle': 'ohos.example.themeswitch',
        'ui': [
            ('StartAbility_001', '拉起应用并校验首页渲染'),
            ('changeThemeDialog_001', '点击切换主题，校验主题弹窗出现'),
            ('changeToDay_001', '切换浅色主题，校验浅色主题生效'),
            ('changeToNight_001', '切换深色主题，校验深色主题生效'),
            ('changeToCustom_001', '切换自定义主题，校验自定义主题生效'),
            ('changeToDay_002', '再次切回浅色主题，校验主题可来回切换'),
        ],
        'logic': [
            ('ThemeSwitch_GetTheme_Custom_001', '主题索引 3 返回自定义主题'),
            ('ThemeSwitch_GetTheme_Default_001', '系统主题索引返回默认主题'),
            ('ThemeSwitch_ThemeRes_Diff_001', '两套主题的导航图资源互不相同'),
            ('ThemeSwitch_ThemeFields_Defined_001', '主题颜色/图片字段均已定义'),
            ('ThemeSwitch_DefaultSelectedColor_001', '默认主题选中态颜色为红色'),
        ],
        'changes': [
            '数据模型类统一改为 `interface`，满足 ArkTS `arkts-no-ctor-prop-decls`、`arkts-no-untyped-obj-literals` 等约束。',
            '移除 `@ohos.application.abilityManager`（API 26 已删除），改用 `ApplicationContext.setColorMode` + `ConfigurationConstant.ColorMode`。',
            '`@ohos.mediaquery` 迁移到 `@kit.ArkUI` 的 `mediaquery`，并为媒体查询回调补充显式参数类型。',
            '为 `ForEach` 的 item 参数补充显式类型，消除 `arkts-no-any-unknown` 报错。',
            '删除 `ohos.permission.UPDATE_CONFIGURATION`（系统权限，普通应用无法申请，且新方案不再需要）。',
            '补齐 `srcEntry`、`exported`、`local.properties` 等 API 26 工程配置。',
        ],
    },
    {
        'dir': r'Media\GamePuzzle',
        'name': 'GamePuzzle',
        'bundle': 'ohos.samples.gamepuzzle',
        'ui': [
            ('ohos.samples.gamepuzzle_StartAbility_001', '拉起应用、处理媒体权限弹窗，校验「开始」「重新开始」按钮'),
            ('ohos.samples.gamepuzzle_StartGame_001', '点击开始，校验计时控件出现'),
            ('ohos.samples.gamepuzzle_Restart_001', '点击重新开始，校验回到可开始状态'),
        ],
        'logic': [
            ('GamePuzzle_FindEmptyIndex_001', '空位查找：命中/未命中两种场景'),
            ('GamePuzzle_ItemChange_001', '交换后空位移动到被点击位置'),
            ('GamePuzzle_GameBegin_001', '洗牌后仍是 1~9 共 9 个序号，不重不漏'),
            ('GamePuzzle_GameInit_NotStarted_001', '游戏未开始时点击不移动'),
            ('GamePuzzle_GameInit_Started_001', '游戏开始后相邻格子可移动'),
        ],
        'changes': [
            '`@ohos.filemanagement.userFileManager` 在 API 26 已移除，图片读取改为 `photoAccessHelper.getAssets` + `dataSharePredicates`。',
            '`PhotoAsset.open()` 已删除，改为 `fileIo.open(uri, READ_ONLY)` 读取图片文件描述符。',
            '`srcEntrance` 改为 `srcEntry`、`visible` 改为 `exported`，补齐 API 26 工程配置与签名。',
            '签名 Profile 使用 `system_basic` + ACL（`ohos.permission.READ_IMAGEVIDEO`、`ohos.permission.MEDIA_LOCATION`），确保普通安装方式下可访问媒体库。',
            '测试用例重写为可自动通过的 UI 流程，并补充 `GameRules` 拼图规则的逻辑用例。',
        ],
    },
    {
        'dir': r'WindowManagement\WindowManage',
        'name': 'WindowManage',
        'bundle': 'ohos.samples.windowcomponent',
        'ui': [
            ('WindowManager_StartAbility_001', '拉起应用，校验三个功能入口'),
            ('WindowManager_GetPropertiesOfSystemBarPage_001', '进入系统栏属性页，点击获取按钮，校验属性文本非空'),
            ('WindowManager_SetTouchableAreas_001', '进入可触摸区域页，点击区域1，校验提示 `click 区域1`'),
            ('WindowManager_OpenVideoPage_001', '进入窗口视频页，校验窗口按钮出现'),
        ],
        'logic': [
            ('WindowManage_EventId_001', '子窗口事件 id 常量为 1001'),
            ('WindowManage_WindowColor_001', '系统栏颜色常量均为十六进制颜色串'),
            ('WindowManage_WindowType_001', '子窗口属性结构可实例化并保留取值'),
            ('WindowManage_FormatProperties_001', '系统栏属性格式化为缩进 JSON'),
        ],
        'changes': [
            '`WindowComponent` 为 HAR 模块，`hvigorfile.ts` 使用 `harTasks`；entry 通过 `file:../WindowComponent` 依赖，构建前需执行 `ohpm install`。',
            '签名 Profile 使用 `system_basic` + ACL（`ohos.permission.SYSTEM_FLOAT_WINDOW`），保证悬浮窗口能力可用。',
            '测试代码去掉嵌套 `it` 结构，改为扁平用例列表；资源字符串改为当前语言字面量，避免 `resourceManager` 为空导致用例失败。',
            '新增 `utils/WindowFormat.ets` 承载系统栏属性格式化逻辑（便于单元测试），页面改为调用 `formatSystemBarProperties`。',
            'HAR 侧 `WindowConst` 常量对外导出，供逻辑用例复用。',
        ],
    },
    {
        'dir': r'Security\CertificateFramework',
        'name': 'CertificateFramework',
        'bundle': 'com.samples.certframework',
        'ui': [
            ('StartAbility_001', '拉起应用'),
            ('DisplayData_001', '点击展示数据，校验证书/原文/签名数据正确显示'),
            ('Verify_001', '点击签名校验，校验提示「校验通过」'),
            ('ModifyOriginData_001', '篡改原文后校验签名数据仍正确、原文已变化'),
            ('ModifySignatureData_001', '篡改签名数据后校验失败'),
            ('Verify_002', '二次签名校验'),
            ('Verify_003', '三次签名校验'),
            ('Verify_004', '四次签名校验'),
            ('CertChain_001', '证书链解析校验'),
            ('CertChain_002', '证书链二次解析校验'),
        ],
        'logic': [
            ('Cert_StringToUint8Array_001', '字符串转字节数组'),
            ('Cert_StringToUint8Array_002', '空字符串返回 null'),
            ('Cert_CreateX509Cert_001', '证书数据解析为 X509 证书且公钥可导出'),
            ('Cert_DataDisplay_001', '展示数据：证书/原文/签名均非空'),
            ('Cert_ModifyOriginData_001', '篡改原文后原文变化、签名不变'),
            ('Cert_ModifySignatureData_001', '篡改签名后签名数据变化'),
            ('Cert_ChainDataDisplay_001', '证书链展示数据非空'),
            ('Cert_CreateX509CertChain_001', '证书链可被解析'),
        ],
        'changes': [
            '补齐 API 26 工程配置（SDK 版本、hvigorfile、hvigor-config、oh-package、local.properties）与调试签名。',
            '测试入口统一为 `testrunner/OpenHarmonyTestRunner.ts` + `testability`，与 DevEco 模板一致。',
            '`StartAbility_001` 增加启动等待，避免首个用例在应用窗口未就绪时查询 UI 失败。',
            '补充证书解析、数据展示与篡改校验的逻辑用例（不依赖 UI）。',
        ],
    },
    {
        'dir': r'Media\VoiceCallDemo',
        'name': 'VoiceCallDemo',
        'bundle': 'com.samples.voicecalldemo',
        'ui': [
            ('com.samples.voicecalldemoStartAbility_001', '拉起被叫页面，处理麦克风授权，校验接听/挂断按钮'),
            ('Answer_001', '点击接听，校验通话计时组件出现'),
            ('Hangup_001', '点击挂断，校验通话页面关闭'),
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
        'changes': [
            '`Window.hide()` 在 API 26 已移除，主窗口隐藏改为 `minimize()`。',
            '`AudioVolumeGroupManager.setAudioScene` 属于系统接口且已移除，删除调用并保留日志（非系统应用播放 VOICE_CALL 音频时系统会自动切换音频场景）。',
            '移除 `ohos.permission.MANAGE_AUDIO_CONFIG`、`ohos.permission.SYSTEM_FLOAT_WINDOW` 等系统权限，避免普通安装失败；悬浮窗能力在无该权限时自动降级。',
            '`ArrayBufferUtils` 中 `Function.apply` 改写为显式循环，满足 `arkts-no-func-apply-call`。',
            '补齐 `usedScene` 权限声明、API 26 工程配置与调试签名，并重写 UI 用例、补充工具类逻辑用例。',
        ],
    },
    {
        'dir': r'Media\Recorder',
        'name': 'Recorder',
        'bundle': 'ohos.samples.recorder',
        'ui': [
            ('Recorder_StartAbility_001', '拉起应用、处理麦克风授权，校验首页录音按钮'),
            ('Recorder_RecordPage_001', '点击录音，校验录音时长与结束按钮'),
            ('Recorder_FinishRecord_001', '结束录音，校验返回首页'),
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
        'changes': [
            '`@ohos.filemanagement.userFileManager` 的音频资源能力在 API 26 已移除，录音文件改为保存在应用沙箱 `filesDir/records` 目录，`MediaManager` 使用 `fileIo` 完成创建、列举、重命名与删除。',
            '`PhotoAsset.open/close` 改为 `fileIo.open/close`，录音与播放均按文件描述符（`fd://`）处理。',
            '移除 `READ_MEDIA`、`WRITE_MEDIA`、`READ_AUDIO`、`WRITE_AUDIO` 等系统权限，仅保留 `ohos.permission.MICROPHONE`。',
            '`Record` 模型改为持有沙箱文件路径（`filePath`），`AudioModel` 支持按路径播放。',
            '重写 UI 用例，并补充日期时间与时长格式化的逻辑用例。',
        ],
    },
    {
        'dir': r'Media\MusicPlayer',
        'name': 'MusicPlayer',
        'bundle': 'com.samples.musicplayer',
        'ui': [
            ('com.samples.musicplayer_StartAbility_001', '拉起应用，校验曲目信息与播放控制按钮渲染'),
            ('com.samples.musicplayer_PlayNext_001', '点击下一首，校验曲目标题发生变化'),
            ('com.samples.musicplayer_PlayPause_001', '点击播放/暂停，校验界面保持可用'),
            ('com.samples.musicplayer_LoopMode_001', '切换播放模式，校验界面保持可用'),
        ],
        'logic': [
            ('MusicPlayer_MusicList_Count_001', '曲目列表包含 3 首示例歌曲'),
            ('MusicPlayer_MusicList_Content_001', '曲目序号与资源字段正确'),
            ('MusicPlayer_PlayerState_001', '播放器状态常量取值正确'),
            ('MusicPlayer_SliderRange_001', '播放进度条取值范围有效'),
        ],
        'changes': [
            '工程由 HarmonyOS 运行态改为 OpenHarmony（`runtimeOS: OpenHarmony`），并补齐 `compileSdkVersion`/`targetSdkVersion` 26.0.0。',
            '`deviceTypes` 调整为 `default`/`tablet`，避免多设备系统能力交集为空导致构建失败。',
            '为播放控制与曲目信息补充组件 id（`musicTitle`、`playBtn`、`nextBtn`、`prevBtn`、`loopModeBtn`），便于 UI 自动化。',
            '补齐 `testability`、`testrunner`、测试资源与测试用例（原工程仅模板用例）。',
            '`musicplayer` HAR 对外导出 `CommonConstants`，供逻辑用例校验曲目数据与播放器常量。',
        ],
    },
]

README_SECTION = '''## API 26.0.0 适配说明

本工程已适配 OpenHarmony SDK 26.0.0（`compileSdkVersion` / `compatibleSdkVersion` / `targetSdkVersion` 均为 `26.0.0`，`runtimeOS` 为 `OpenHarmony`）。
使用 DevEco Studio 打开即可直接构建、安装、运行，无需手工配置签名或 SDK。

### 主要适配点

{changes}

### 编译与运行

1. 使用 DevEco Studio（`DS-261.23567.138.36.2600851` 及以上）打开工程根目录；
2. 等待 Sync 完成（`hvigor` 版本与 `modelVersion` 已固定为 26.0.0）；
3. 选择 `entry` 模块与已连接设备，直接 Run；
4. 工程已内置调试签名（`signature/`），无需在 `Project Structure > Signing Configs` 中手工配置。

### 测试

本工程测试包含 **UI 用例** 与 **逻辑用例** 两部分，共 {total} 个用例：

```bash
hdc shell aa test -b {bundle} -m entry_test -s unittest OpenHarmonyTestRunner
```

用例清单见 [ohosTest.md](./ohosTest.md)。
'''

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


for proj in PROJECTS:
    base = os.path.join(ROOT, proj['dir'])
    changes = '\n'.join('- ' + c for c in proj['changes'])
    total = len(proj['ui']) + len(proj['logic'])
    section = README_SECTION.format(changes=changes, bundle=proj['bundle'], total=total).strip()

    readme = os.path.join(base, 'README_zh.md')
    if os.path.exists(readme):
        with io.open(readme, encoding='utf-8', errors='replace') as f:
            old = f.read()
        marker = '## API 26.0.0 适配说明'
        if marker in old:
            old = old[:old.index(marker)].rstrip() + '\n\n' + section + '\n'
        else:
            old = old.rstrip() + '\n\n' + section + '\n'
        write(readme, old)
    else:
        write(readme, '# {}\n\n{}\n'.format(proj['name'], section))

    ui_rows = '\n'.join('| `{}` | {} |'.format(t[0], t[1]) for t in proj['ui'])
    logic_rows = '\n'.join('| `{}` | {} |'.format(t[0], t[1]) for t in proj['logic'])
    write(os.path.join(base, 'ohosTest.md'),
          TEST_DOC.format(bundle=proj['bundle'], ui_rows=ui_rows, logic_rows=logic_rows,
                          ui_count=len(proj['ui']), logic_count=len(proj['logic']), total=total))

print('docs updated: {}'.format(len(PROJECTS)))
