# -*- coding: utf-8 -*-
"""生成九个工程 API 26 适配情况汇总表（表头与用户模板一致）。"""
import os

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

OUT = r'C:\Users\zhong\Desktop\XTS九个工程适配情况汇总.xlsx'

HEADERS = ['编号', '一级分类', '工程路径', 'runtimeOS', 'compileSdk', 'compatibleSdk',
           '建议目标', '测试用例覆盖（ohosTest）', '完成情况', '存在无法通过问题及其原因', '预计修改代码量']

ROWS = [
    [74, 'SystemFeature', 'SystemFeature/Media/Camera', 'OpenHarmony', '26.0.0', '26.0.0', 'API 26',
     'UI 5 条 + 逻辑 11 条（1 文件/109 行），共 16 条', '已完成：16/16 通过，README/ohosTest.md 已更新',
     '无', '17 文件，+891/−445；新增 2 文件 219 行'],
    [75, 'SystemFeature', 'SystemFeature/Media/GamePuzzle', 'OpenHarmony', '26.0.0', '26.0.0', 'API 26',
     'UI 11 条 + 逻辑 5 条（1 文件/153 行），共 16 条', '已完成：16/16 通过，README/ohosTest.md 已更新',
     '无（已内置 system_basic + ACL 签名）', '5 文件，+453/−192；新增 3 文件 165 行'],
    [76, 'SystemFeature', 'SystemFeature/Media/MusicPlayer', 'OpenHarmony', '26.0.0', '26.0.0', 'API 26',
     'UI 4 条 + 逻辑 4 条（1 文件/98 行），共 8 条', '已完成：8/8 通过，README/ohosTest.md 已更新',
     '无（“其他功能菜单”为样例 TODO，点击弹提示）', '8 文件，+201/−82；新增 2 文件 115 行'],
    [77, 'SystemFeature', 'SystemFeature/Media/Recorder', 'OpenHarmony', '26.0.0', '26.0.0', 'API 26',
     'UI 14 条 + 逻辑 7 条（1 文件/152 行），共 21 条', '已完成：21/21 通过，README/ohosTest.md 已更新',
     '无（列表/页面切换已优化）', '19 文件，+911/−704；新增 1 文件 152 行'],
    [78, 'SystemFeature', 'SystemFeature/Media/VoiceCallDemo', 'OpenHarmony', '26.0.0', '26.0.0', 'API 26',
     'UI 5 条 + 逻辑 7 条（1 文件/151 行），共 12 条', '已完成：12/12 通过，README/ohosTest.md 已更新',
     '无（悬浮窗需系统权限，未申请时降级为最小化）', '10 文件，+299/−231；新增 1 文件 151 行'],
    [79, 'SystemFeature', 'SystemFeature/Notification/Publish', 'OpenHarmony', '26.0.0', '26.0.0', 'API 26',
     'UI 2 条 + 逻辑 4 条（1 文件/105 行），共 6 条', '已完成：6/6 通过，README/ohosTest.md 已更新',
     '无（订阅相关系统 API 已移除，示例改为通知发布）', '7 文件，+231/−118；新增 1 文件 105 行'],
    [80, 'SystemFeature', 'SystemFeature/ResourceAllocation/ApplicationThemeSwitch', 'OpenHarmony', '26.0.0', '26.0.0',
     'API 26', 'UI 6 条 + 逻辑 5 条（1 文件/114 行），共 11 条', '已完成：11/11 通过，README/ohosTest.md 已更新',
     '无', '14 文件，+359/−290；新增 3 文件 126 行'],
    [81, 'SystemFeature', 'SystemFeature/Security/CertificateFramework', 'OpenHarmony', '26.0.0', '26.0.0', 'API 26',
     'UI 10 条 + 逻辑 8 条（1 文件/192 行），共 18 条', '已完成：18/18 通过，README/ohosTest.md 已更新',
     '无', '6 文件，+231/−145；新增 1 文件 192 行'],
    [82, 'SystemFeature', 'SystemFeature/WindowManagement/WindowManage', 'OpenHarmony', '26.0.0', '26.0.0', 'API 26',
     'UI 13 条 + 逻辑 4 条（1 文件/121 行），共 17 条', '已完成：17/17 通过，README/ohosTest.md 已更新',
     '无（拉起悬浮应用依赖外部 WindowRatio，未安装时提示）', '12 文件，+644/−377；新增 5 文件 173 行'],
]

HEADER_FILL = PatternFill('solid', fgColor='1F4E79')
HEADER_FONT = Font(name='微软雅黑', size=10, bold=True, color='FFFFFF')
BODY_FONT = Font(name='微软雅黑', size=9)
THIN = Side(style='thin', color='BFBFBF')
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

wb = Workbook()
ws = wb.active
ws.title = 'API26适配情况'

ws.append(HEADERS)
for cell in ws[1]:
    cell.fill = HEADER_FILL
    cell.font = HEADER_FONT
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    cell.border = BORDER

for row in ROWS:
    ws.append(row)

for r in range(2, ws.max_row + 1):
    for c in range(1, len(HEADERS) + 1):
        cell = ws.cell(row=r, column=c)
        cell.font = BODY_FONT
        cell.border = BORDER
        cell.alignment = Alignment(
            horizontal='center' if c in (1, 4, 5, 6, 7) else 'left',
            vertical='center', wrap_text=True)

widths = [7, 12, 40, 12, 11, 13, 9, 34, 32, 34, 32]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.row_dimensions[1].height = 34
for r in range(2, ws.max_row + 1):
    ws.row_dimensions[r].height = 42
ws.freeze_panes = 'A2'
ws.auto_filter.ref = 'A1:K10'

wb.save(OUT)

# 校验
from openpyxl import load_workbook
check = load_workbook(OUT)
sheet = check['API26适配情况']
assert sheet.max_row == 10 and sheet.max_column == 11, (sheet.max_row, sheet.max_column)
assert sheet['A1'].value == '编号' and sheet['K1'].value == '预计修改代码量'
assert sheet['A2'].value == 74 and sheet['A10'].value == 82
assert sheet['C10'].value == 'SystemFeature/WindowManagement/WindowManage'
assert sheet['H2'].value.startswith('UI 5 条')
print('saved and verified:', OUT, os.path.getsize(OUT), 'bytes')
