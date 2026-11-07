# -*- coding: utf-8 -*-
import io

PATH = r'D:\XTS\code\SystemFeature\ResourceAllocation\ApplicationThemeSwitch\README_zh.md'
text = io.open(PATH, encoding='utf-8').read()

text = text.replace(
    '通过[@ohos.application.abilityManager](https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/reference/apis-ability-kit/js-apis-application-abilityManager-sys.md) 能力，对Ability状态进行修改：其中AbilityManager.updateConfiguration()通过修改colorMode属性来更新配置系统主题颜色。',
    '通过 [ApplicationContext.setColorMode](https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/reference/apis-ability-kit/js-apis-inner-application-applicationContext.md) 能力切换系统深浅色模式：调用 `setColorMode(ConfigurationConstant.ColorMode.COLOR_MODE_DARK / COLOR_MODE_LIGHT)` 更新应用配置，使 dark/light 资源生效。')

text = text.replace(
    '  * 4）定义事件修改变量theme的值，如果是系统主题（dark，light），调用AbilityManager.updateConfiguration()，通过修改colorMode属性来更新配置系统主题颜色（0：深夜 1：白天）',
    '  * 4）定义事件修改变量theme的值，如果是系统主题（dark，light），调用 ApplicationContext.setColorMode() 并传入 ConfigurationConstant.ColorMode 来更新系统主题颜色（0：深夜 1：白天）')

perm_start = text.find('### 相关权限')
perm_end = text.find('### 依赖', perm_start)
assert perm_start != -1 and perm_end != -1
text = text[:perm_start] + '''### 相关权限

本示例不需要申请系统权限（原 `ohos.permission.UPDATE_CONFIGURATION` 已随旧接口一并移除）。

''' + text[perm_end:]

con_start = text.find('### 约束与限制')
con_end = text.find('### 下载', con_start)
assert con_start != -1 and con_end != -1
text = text[:con_start] + '''### 约束与限制

1. 本示例仅支持标准系统上运行；
2. 本示例已适配 OpenHarmony API 26.0.0 版本 SDK（`compileSdkVersion` / `compatibleSdkVersion` / `targetSdkVersion` = `26.0.0`）；
3. 本示例需要使用 DevEco Studio（Build Version: DS-261.23567.138.36.2600851）及以上版本才可编译运行；
4. 本示例不再使用 `@ohos.application.abilityManager` 等系统接口，无需替换 Full SDK，也不需要 system_basic 级别签名。

''' + text[con_end:]

io.open(PATH, 'w', encoding='utf-8', newline='\n').write(text)
print('themeswitch readme updated')
