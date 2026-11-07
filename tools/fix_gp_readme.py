# -*- coding: utf-8 -*-
import io

# ---------- 中文 README ----------
PATH = r'D:\XTS\code\SystemFeature\Media\GamePuzzle\README_zh.md'
text = io.open(PATH, encoding='utf-8').read()

text = text.replace(
    '1. 使用预置相机拍照后启动应用，应用首页会读取设备内的图片文件并展示获取到的第一个图片，没有图片时图片位置显示空白；',
    '1. 启动应用后，首页会读取设备相册中的图片并展示获取到的第一张图片；相册为空时图片位置显示空白（可先使用系统相机拍摄或导入图片）；')

text = text.replace(
    '  + 获取本地图片：首先使用getMediaLibrary获取媒体库实例，然后使用getFileAssets方法获取文件资源，最后使用getAllObject获取检索结果中的所有文件资产方便展示；',
    '  + 获取本地图片：首先使用 photoAccessHelper.getPhotoAccessHelper 获取媒体库实例，然后使用 getAssets 方法获取图片资源，最后使用 getAllObjects 获取检索结果中的所有图片资产方便展示；')

text = text.replace(
    '  + 图片编辑：首先使用createImagePacker创建ImagePacker实例，然后使用fileAsset.open打开文件，调用createImageSource接口创建图片源实例方便操作图片，接下来使用getImageInfo方法获取图片大小便于分割，最后使用createPixelMap方法传入每一份的尺寸参数完成图片裁剪。',
    '  + 图片编辑：首先使用createImagePacker创建ImagePacker实例，然后使用 fileIo.open 打开图片文件，调用createImageSource接口创建图片源实例方便操作图片，接下来使用getImageInfo方法获取图片大小便于分割，最后使用createPixelMap方法传入每一份的尺寸参数完成图片裁剪。')

text = text.replace(
    '[ohos.permission.READ_IMAGEVIDEO](https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/security/AccessToken/permissions-for-system-apps.md#ohospermissionread_imagevideo)',
    '[ohos.permission.READ_IMAGEVIDEO](https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/security/AccessToken/permissions-for-system-apps.md#ohospermissionread_imagevideo)（工程内置的调试签名 Profile 已配置 `system_basic` + ACL，无需手动配置签名）')

con_start = text.find('### 约束与限制')
con_end = text.find('### 下载', con_start)
assert con_start != -1 and con_end != -1
text = text[:con_start] + '''### 约束与限制

1. 本示例仅支持标准系统上运行；
2. 本示例已适配 OpenHarmony API 26.0.0 版本 SDK（`compileSdkVersion` / `compatibleSdkVersion` / `targetSdkVersion` = `26.0.0`）；
3. 本示例需要使用 DevEco Studio（Build Version: DS-261.23567.138.36.2600851）及以上版本才可编译运行；
4. 工程内置的调试签名 Profile 已包含 `ohos.permission.READ_IMAGEVIDEO`、`ohos.permission.MEDIA_LOCATION` 的 ACL，可直接安装运行，无需替换 Full SDK。

''' + text[con_end:]

io.open(PATH, 'w', encoding='utf-8', newline='\n').write(text)

# ---------- 英文 README ----------
PATH_EN = r'D:\XTS\code\SystemFeature\Media\GamePuzzle\README.md'
en = io.open(PATH_EN, encoding='utf-8').read()
en = en.replace(
    '2. This sample demonstrates the stage model, which supports only API version 9.',
    '2. This sample uses the stage model and has been adapted to OpenHarmony API 26.0.0 (compileSdkVersion / compatibleSdkVersion / targetSdkVersion = 26.0.0).')
io.open(PATH_EN, 'w', encoding='utf-8', newline='\n').write(en)
print('gamepuzzle readme updated')
