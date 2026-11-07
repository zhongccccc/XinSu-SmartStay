# -*- coding: utf-8 -*-
"""测试模式：人脸页自动放行，不采集不比对。"""
# ---------- 后端：face_sim 开关 ----------
P = r"E:\zhikong\app\backend\main.py"
s = open(P, encoding="utf-8").read()

OLD = '''    def _face(self):
        d = self._body()
        if APP.ctrl.state["step"] != "face":
            return APP.ctrl.snapshot()
        path = None
        if d.get("capture", True):'''
NEW = '''    def _face(self):
        d = self._body()
        if APP.ctrl.state["step"] != "face":
            return APP.ctrl.snapshot()
        # 测试模式：不采集画面，直接放行（客户要的"走个样子"）
        if CONF.get("kiosk", {}).get("face_sim", True) and not d.get("real"):
            APP.ctrl.on_face(None, 0.96)
            return APP.ctrl.snapshot()
        path = None
        if d.get("capture", True):'''

if "face_sim" not in s and OLD in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("后端已加 face_sim")
else:
    print("后端:", "已存在" if "face_sim" in s else "未匹配")

# ---------- 前端：进入人脸页自动放行 ----------
J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()

if "autoFaceOnce" not in js:
    OLD2 = """    if (LAST_STEP !== 'face') {
      img.src = img.dataset.src + '?t=' + Date.now();
      if (window.__guardCam) window.__guardCam();
    }"""
    NEW2 = """    if (LAST_STEP !== 'face') {
      img.src = img.dataset.src + '?t=' + Date.now();
      if (window.__guardCam) window.__guardCam();
      /* 测试模式：进来 1.5 秒后自动"识别"通过 */
      window.__autoFaceOnce = window.__autoFaceOnce || false;
      if (!window.__autoFaceOnce) {
        window.__autoFaceOnce = true;
        const bf = $('#btnFace');
        if (bf) { bf.disabled = true; bf.textContent = '识别中…'; }
        setTimeout(async () => {
          if (!STATE || STATE.step !== 'face') return;
          try { await api('/api/face', { capture: false }); } catch (_) {}
        }, 1500);
      }
    }"""
    if OLD2 in js:
        js = js.replace(OLD2, NEW2, 1)
        print("前端已加自动放行")
    else:
        print("前端未匹配")
else:
    print("前端已存在")
open(J, "w", encoding="utf-8").write(js)
