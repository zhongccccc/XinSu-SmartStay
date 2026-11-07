# -*- coding: utf-8 -*-
import io

PATH = r'D:\XTS\code\SystemFeature\WindowManagement\WindowManage\README_zh.md'
text = io.open(PATH, encoding='utf-8').read()

dep_start = text.find('### 依赖')
dep_end = text.find('### 约束与限制', dep_start)
assert dep_start != -1 and dep_end != -1
text = text[:dep_start] + '''### 依赖

不涉及必需依赖。

> 子窗口页面中的“拉起悬浮应用”按钮会以悬浮窗模式拉起 `com.samples.windowratio`（WindowRatio 示例），该示例不在本工程内；未安装时点击仅记录启动失败日志，不影响本示例其他功能与自动化用例。

''' + text[dep_end:]

con_start = text.find('### 约束与限制')
con_end = text.find('### 下载', con_start)
assert con_start != -1 and con_end != -1
text = text[:con_start] + '''### 约束与限制

1. 本示例仅支持标准系统上运行；
2. 本示例已适配 OpenHarmony API 26.0.0 版本 SDK（`compileSdkVersion` / `compatibleSdkVersion` / `targetSdkVersion` = `26.0.0`）；
3. 本示例需要使用 DevEco Studio（Build Version: DS-261.23567.138.36.2600851）及以上版本才可编译运行；
4. 本示例无需替换 Full SDK；`window.setTouchableAreas` 在当前 SDK 中可直接编译使用；
5. 工程内置的调试签名 Profile 已为 `ohos.permission.SYSTEM_FLOAT_WINDOW` 配置 `system_basic` + ACL，可直接安装运行，无需手动配置签名。

''' + text[con_end:]

text = text.replace(
    '允许应用使用悬浮窗的能力：[ohos.permission.SYSTEM_FLOAT_WINDOW](https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/security/AccessToken/permissions-for-system-apps.md#ohospermissionsystem_float_window)',
    '允许应用使用悬浮窗的能力：[ohos.permission.SYSTEM_FLOAT_WINDOW](https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/security/AccessToken/permissions-for-system-apps.md#ohospermissionsystem_float_window)（工程内置的调试签名 Profile 已配置 `system_basic` + ACL，无需手动配置）')

io.open(PATH, 'w', encoding='utf-8', newline='\n').write(text)
print('windowmanage readme updated')
