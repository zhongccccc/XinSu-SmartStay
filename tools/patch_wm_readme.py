import io
p = r'D:\XTS\code\SystemFeature\WindowManagement\WindowManage\README_zh.md'
t = io.open(p, encoding='utf-8').read()
old = "5.点击视频屏幕拉起小窗口视频；若设备已安装 WindowRatio 示例，可点击小窗口中的“拉起悬浮应用”按钮以悬浮窗模式拉起该示例（未安装时仅提示启动失败）。"
new = ("5.点击视频屏幕拉起小窗口视频；若设备已安装 WindowRatio 示例，可点击小窗口中的“拉起悬浮应用”按钮以悬浮窗模式拉起该示例"
       "（未安装时会提示“未安装 WindowRatio 示例应用”）。\n"
       "6.子窗口打开时，按返回键会先关闭子窗口；再次按返回键退出视频页回到首页。")
assert old in t
t = t.replace(old, new)
old2 = "未安装时点击仅记录启动失败日志，不影响本示例其他功能与自动化用例。"
new2 = "未安装时点击会提示“未安装 WindowRatio 示例应用”，不影响本示例其他功能与自动化用例。"
assert old2 in t
t = t.replace(old2, new2)
io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('README_zh updated')
