# -*- coding: utf-8 -*-
"""人脸核验按钮加 12 秒超时，避免摄像头卡住时界面一直转圈。"""
J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()

OLD = """$('#btnFace').onclick = async () => {
  const b = $('#btnFace'); b.disabled = true; b.textContent = '识别中…';
  await api('/api/face', { capture: true });"""
NEW = """$('#btnFace').onclick = async () => {
  const b = $('#btnFace'); b.disabled = true; b.textContent = '识别中…';
  let done = false;
  const guard = setTimeout(() => {
    if (done) return;
    b.disabled = false; b.textContent = '开始人脸核验';
    toast('摄像头无响应，请重试或联系工作人员');
  }, 12000);
  try {
    await api('/api/face', { capture: true });
  } catch (_) {
    toast('网络异常，请重试');
  } finally {
    done = true; clearTimeout(guard);
    b.disabled = false; b.textContent = '开始人脸核验';
  }"""

if OLD in js:
    js = js.replace(OLD, NEW, 1)
    open(J, "w", encoding="utf-8").write(js)
    print("人脸按钮已加超时")
else:
    print("未匹配，检查行内容")
    idx = js.find("btnFace")
    print(js[idx-80:idx+260] if idx > 0 else "(找不到 btnFace)")
