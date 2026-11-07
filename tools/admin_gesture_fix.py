# -*- coding: utf-8 -*-
"""管理员手势改到「连点右下角版本号 5 次」，把 logo 长按还给"退出应用"。
"""
J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()

# 1) 恢复 logo 长按只做退出（去掉我加的 admin/staff）
OLD = """  let t = null;
  const start = () => {
    clearTimeout(t);
    t = setTimeout(() => {
      document.body.classList.add('staff');
      document.body.classList.add('admin');
      try { toast('已进入管理员模式'); } catch (_) {}
    }, 4000);
  };"""
NEW = """  /* 长按 logo：只负责"退出应用"（管理员入口见下方 5 连点版本号） */
  let t = null;
  const start = () => {
    clearTimeout(t);
    t = setTimeout(() => {
      document.body.classList.add('staff');
    }, 3000);
  };"""
if OLD in js:
    js = js.replace(OLD, NEW, 1)
    print("logo 长按已恢复为退出应用")

# 2) 5 连点右下角版本号 -> 管理员模式
if "bindAdminGesture" not in js:
    js += '''

/* ---------- 管理员入口：连点右下角版本号 5 次 ---------- */
(function bindAdminGesture() {
  let taps = 0;
  let timer = null;

  document.addEventListener('click', (ev) => {
    const t = ev.target;
    if (!t || !t.classList || !t.classList.contains('ver')) return;
    taps += 1;
    clearTimeout(timer);
    timer = setTimeout(() => { taps = 0; }, 2500);
    if (taps >= 5) {
      taps = 0;
      document.body.classList.add('staff');
      document.body.classList.add('admin');
      try { toast('已进入管理员模式'); } catch (_) {}
    }
  });
})();
'''
    print("已加 5 连点入口")

open(J, "w", encoding="utf-8").write(js)
print("done")
