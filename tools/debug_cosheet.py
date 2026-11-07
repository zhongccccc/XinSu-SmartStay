# -*- coding: utf-8 -*-
"""调试：?cosheet=1 自动打开退房列表（便于截图）。"""
J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()

if "cosheet=1" not in js:
    js += '''

/* 调试：?cosheet=1 自动打开退房列表 */
if (/[?&]cosheet=1/.test(location.search)) {
  setTimeout(() => {
    if (window.__openCoSheet) window.__openCoSheet();
  }, 1500);
}
'''
    open(J, "w", encoding="utf-8").write(js)
    print("已加 ?cosheet=1")
else:
    print("已存在")
