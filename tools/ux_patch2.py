# -*- coding: utf-8 -*-
"""隐藏调试按钮（仅 ?staff=1 显示）+ 恢复 board 传输。"""
C = r"E:\zhikong\app\web\style.css"
cs = open(C, encoding="utf-8").read()
if "staff-only" not in cs:
    cs += '''

/* 调试/前台功能默认隐藏，?staff=1 时显示 */
.done-actions .ghost{display:none}
body.staff .done-actions .ghost{display:inline-flex}
'''
    open(C, "w", encoding="utf-8").write(cs)
    print("CSS ok")

J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()
if "classList.add('staff')" not in js:
    js += '''

/* 前台模式：URL 带 ?staff=1 才显示调试按钮 */
if (/[?&]staff=1/.test(location.search)) document.body.classList.add('staff');
'''
    open(J, "w", encoding="utf-8").write(js)
    print("JS ok")
