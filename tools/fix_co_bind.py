# -*- coding: utf-8 -*-
"""避免重复绑定：旧按钮改为暴露函数，由引导页调用。"""
J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()

old = "if (btn) btn.addEventListener('click', () => { fill(); sheet().classList.add('on'); });"
new = "if (btn) window.__openCoSheet = () => { fill(); sheet().classList.add('on'); };"
if old in js:
    js = js.replace(old, new, 1)
    print("旧绑定已改为函数")

old2 = """  const pick = document.getElementById('coGuidePick');
  if (pick) pick.onclick = () => {
    guide.classList.remove('on');
    if (sheet) sheet.classList.add('on');
  };"""
new2 = """  const pick = document.getElementById('coGuidePick');
  if (pick) pick.onclick = () => {
    guide.classList.remove('on');
    if (window.__openCoSheet) window.__openCoSheet();
    else if (sheet) sheet.classList.add('on');
  };"""
if old2 in js:
    js = js.replace(old2, new2, 1)
    print("引导页已接入填充函数")

open(J, "w", encoding="utf-8").write(js)
