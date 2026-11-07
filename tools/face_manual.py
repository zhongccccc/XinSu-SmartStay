# -*- coding: utf-8 -*-
"""1) 身份证提示：保持 2 秒 -> 6 秒
   2) 人脸页：取消自动跳过，必须点「立即识别」，点击后 5 秒再进下一步
"""
J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()

# ---------- 1) 身份证 6 秒 ----------
js = js.replace("'芯片面朝上，平放于感应区，保持 2 秒'",
                "'芯片面朝上，平放于感应区，保持 6 秒'")
print("[1] 身份证提示改为 6 秒")

# ---------- 2) 去掉自动识别 ----------
OLD_AUTO = """      /* 测试模式：进来 1.5 秒后自动"识别"通过 */
      window.__autoFaceOnce = window.__autoFaceOnce || false;
      if (!window.__autoFaceOnce) {
        window.__autoFaceOnce = true;
        const bf = $('#btnFace');
        if (bf) { bf.disabled = true; bf.textContent = '识别中…'; }
        setTimeout(async () => {
          if (!STATE || STATE.step !== 'face') return;
          try { await api('/api/face', { capture: true }); } catch (_) {}
        }, 2000);
      }"""
NEW_AUTO = """      /* 人脸：不自动通过，必须由用户点「立即识别」 */
      const bf = $('#btnFace');
      if (bf) { bf.disabled = false; bf.textContent = '立即识别'; }"""
if OLD_AUTO in js:
    js = js.replace(OLD_AUTO, NEW_AUTO, 1)
    print("[2] 已取消自动识别")
else:
    print("[2] 未匹配自动识别代码")

# 离开人脸页时复位按钮
js = js.replace("""    const bf = $('#btnFace');
    if (bf) { bf.disabled = false; bf.textContent = '开始人脸核验'; }""",
"""    const bf = $('#btnFace');
    if (bf) { bf.disabled = false; bf.textContent = '立即识别'; }""")

# ---------- 3) 按钮点击：5 秒后进入下一步 ----------
if "bindFaceCapture" not in js:
    js += '''

/* ---------- 人脸：点「立即识别」→ 5 秒后进入下一步 ---------- */
(function bindFaceCapture() {
  const btn = document.getElementById('btnFace');
  if (!btn) return;
  if (btn.dataset.bound === '1') return;
  btn.dataset.bound = '1';

  btn.addEventListener('click', async () => {
    if (btn.disabled) return;
    if (!STATE || STATE.step !== 'face') return;

    btn.disabled = true;
    const hint = document.getElementById('faceHint');
    const old = hint ? hint.textContent : '';
    let left = 5;
    if (hint) hint.textContent = '正在识别… ' + left + ' 秒';

    const timer = setInterval(() => {
      left -= 1;
      if (left > 0 && hint) hint.textContent = '正在识别… ' + left + ' 秒';
      if (left <= 0) clearInterval(timer);
    }, 1000);

    /* 5 秒后提交识别结果 */
    setTimeout(async () => {
      clearInterval(timer);
      try {
        await api('/api/face', { capture: true });
      } catch (_) {
        btn.disabled = false;
        btn.textContent = '立即识别';
        if (hint) hint.textContent = old || '识别失败，请重试';
      }
    }, 5000);
  });
})();
'''
    print("[3] 已加「立即识别」按钮逻辑")

open(J, "w", encoding="utf-8").write(js)

# ---------- 4) HTML：按钮文字 + 身份证提示 ----------
H = r"E:\zhikong\app\web\index.html"
h = open(H, encoding="utf-8").read()
h = h.replace('保持 2 秒', '保持 6 秒')
h2 = h.replace('>开始人脸核验<', '>立即识别<').replace('>开始识别<', '>立即识别<')
if h2 != h:
    print("[4] 按钮文字已改为「立即识别」")
open(H, "w", encoding="utf-8").write(h2)
print("done")
