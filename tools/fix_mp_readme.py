# -*- coding: utf-8 -*-
import io

PATH = r'D:\XTS\code\SystemFeature\Media\MusicPlayer\README.md'
text = io.open(PATH, encoding='utf-8').read()

# 1) 更新“约束与限制”中的版本信息
text = text.replace(
    '2.本示例为Stage模型，支持API12版本SDK，SDK版本号（API Version 12 Release）。',
    '2.本示例为 Stage 模型，已适配 OpenHarmony API 26.0.0 版本 SDK（`compileSdkVersion` / `compatibleSdkVersion` / `targetSdkVersion` = `26.0.0`）。')
text = text.replace(
    '3.本示例需要使用DevEco Studio 5.0.0 Release 才可编译运行。',
    '3.本示例需要使用 DevEco Studio（Build Version: DS-261.23567.138.36.2600851）及以上版本才可编译运行。')

# 2) 把英文适配章节替换为中文（README.md 正文为中文）
start = text.find('## API 26.0.0 Adaptation')
if start != -1:
    text = text[:start] + '''## API 26.0.0 适配说明

本工程已适配 OpenHarmony SDK 26.0.0（`compileSdkVersion` / `compatibleSdkVersion` / `targetSdkVersion` 均为 `26.0.0`，`runtimeOS` 为 `OpenHarmony`）。
使用 DevEco Studio 打开即可直接构建、安装、运行，无需手工配置签名或 SDK。

### 主要适配点

- 工程由 HarmonyOS 运行态改为 OpenHarmony（`runtimeOS: OpenHarmony`），并补齐 `compileSdkVersion` / `targetSdkVersion` 26.0.0。
- `deviceTypes` 调整为 `default` / `tablet`，避免多设备系统能力交集为空导致构建失败。
- 为播放控制与曲目信息补充组件 id（`musicTitle`、`playBtn`、`nextBtn`、`prevBtn`、`loopModeBtn`），便于 UI 自动化。
- 补齐 `testability`、`testrunner`、测试资源与测试用例（原工程仅模板用例）。
- `musicplayer` HAR 对外导出 `CommonConstants`，供逻辑用例校验曲目数据与播放器常量。

### 编译与运行

1. 使用 DevEco Studio（`DS-261.23567.138.36.2600851` 及以上）打开工程根目录；
2. 等待 Sync 完成（`hvigor` 版本与 `modelVersion` 已固定为 26.0.0）；
3. 选择 `entry` 模块与已连接设备，直接 Run；
4. 工程已内置调试签名（`signature/`），无需在 `Project Structure > Signing Configs` 中手工配置。

### 测试

本工程测试包含 **UI 用例** 与 **逻辑用例** 两部分，共 8 个用例：

```bash
hdc shell aa test -b com.samples.musicplayer -m entry_test -s unittest OpenHarmonyTestRunner
```

用例清单见 [ohosTest.md](./ohosTest.md)。
'''

io.open(PATH, 'w', encoding='utf-8', newline='\n').write(text)
print('musicplayer README.md updated')
