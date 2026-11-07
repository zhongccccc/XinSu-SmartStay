# -*- coding: utf-8 -*-
"""调试：URL 带 ?admin=1 直接进管理员模式（便于截图/演示）。"""
J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()

OLD = "if (/[?&]staff=1/.test(location.search)) document.body.classList.add('staff');"
NEW = """if (/[?&]staff=1/.test(location.search)) document.body.classList.add('staff');
if (/[?&]admin=1/.test(location.search)) {
  document.body.classList.add('staff');
  document.body.classList.add('admin');
}"""

if "admin=1" not in js and OLD in js:
    js = js.replace(OLD, NEW, 1)
    open(J, "w", encoding="utf-8").write(js)
    print("已加 ?admin=1")
else:
    print("状态:", "已存在" if "admin=1" in js else "未匹配")
