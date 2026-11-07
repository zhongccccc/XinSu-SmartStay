# -*- coding: utf-8 -*-
"""客房环境面板改为前台模式专属 + 长按 logo 进入前台模式。"""
C = r"E:\zhikong\app\web\style.css"
cs = open(C, encoding="utf-8").read()
if "staff-hide-env" not in cs:
    cs += '''

/* 客房环境属于前台功能：客人界面隐藏，前台模式才显示 */
.env-panel{display:none}
.envchip{display:none}
body.staff .env-panel{display:block}
body.staff .envchip{display:block}

/* 前台模式标记 */
body.staff .brand .logo{box-shadow:0 0 0 2px #ffb347 inset}
body.staff .brand-txt span::after{content:" · 前台模式";color:#ffb347}
'''
    open(C, "w", encoding="utf-8").write(cs)
    print("CSS 已改为前台专属")

J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()
if "bindStaffLongPress" not in js:
    js += '''

/* 长按 logo 3 秒进入前台模式（现场无法输 URL 时用） */
(function bindStaffLongPress() {
  const logo = document.querySelector('.brand .logo');
  if (!logo) return;
  let t = null;
  const start = () => {
    clearTimeout(t);
    t = setTimeout(() => {
      document.body.classList.add('staff');
      try { toast('已进入前台模式'); } catch (_) {}
    }, 3000);
  };
  const stop = () => clearTimeout(t);
  logo.addEventListener('mousedown', start);
  logo.addEventListener('touchstart', start, { passive: true });
  logo.addEventListener('mouseup', stop);
  logo.addEventListener('mouseleave', stop);
  logo.addEventListener('touchend', stop);
})();
'''
    open(J, "w", encoding="utf-8").write(js)
    print("长按进入前台模式 已加")
