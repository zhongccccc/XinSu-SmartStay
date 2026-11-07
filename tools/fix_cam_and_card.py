# -*- coding: utf-8 -*-
"""1) 恢复摄像头；2) 人脸页停留 2 秒再自动跳转；3) 房卡步骤延长到 45 秒"""
import re

# ---------- 1) 摄像头恢复 ----------
J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()

OLD_T = """        setTimeout(async () => {
          if (!STATE || STATE.step !== 'face') return;
          try { await api('/api/face', { capture: false }); } catch (_) {}
        }, 1500);"""
NEW_T = """        setTimeout(async () => {
          if (!STATE || STATE.step !== 'face') return;
          try { await api('/api/face', { capture: true }); } catch (_) {}
        }, 2000);"""
if OLD_T in js:
    js = js.replace(OLD_T, NEW_T, 1)
    print("[1] 人脸页改为停留 2 秒（并走真实采集路径）")

open(J, "w", encoding="utf-8").write(js)

# ---------- 2) 房卡步骤 20 秒 -> 45 秒 ----------
M = r"E:\zhikong\app\backend\core\model.py"
m = open(M, encoding="utf-8").read()
if "args=(20,)" in m:
    m = m.replace("args=(20,)", "args=(45,)", 1)
    open(M, "w", encoding="utf-8").write(m)
    print("[2] 房卡步骤超时 20s -> 45s")
else:
    print("[2] 未找到 args=(20,)")
