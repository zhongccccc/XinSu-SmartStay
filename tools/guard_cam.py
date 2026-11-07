# -*- coding: utf-8 -*-
"""人脸页摄像头流加超时保护，避免流卡死时渲染进程空转。"""
J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()

if "guardCamStream" not in js:
    js += '''

/* 摄像头流保护：4 秒内没出画就切到降级提示，并停止重试，避免渲染进程空转 */
(function guardCamStream() {
  const img = document.getElementById('camImg');
  const fb = document.getElementById('camFallback');
  if (!img) return;
  let tries = 0;

  const showFallback = (msg) => {
    img.style.display = 'none';
    if (fb) { fb.style.display = 'flex'; fb.textContent = msg || '摄像头暂时不可用'; }
  };

  img.addEventListener('load', () => {
    tries = 0;
    clearTimeout(window.__camTimer);
    img.style.display = '';
    if (fb) fb.style.display = 'none';
  });

  img.addEventListener('error', () => {
    tries += 1;
    if (tries >= 2) { showFallback('摄像头暂时不可用，请联系工作人员'); return; }
    setTimeout(() => { img.src = img.dataset.src + '?t=' + Date.now(); }, 1500);
  });

  window.__guardCam = () => {
    clearTimeout(window.__camTimer);
    window.__camTimer = setTimeout(() => {
      if (!img.complete || img.naturalWidth === 0) {
        showFallback('摄像头画面加载超时');
        img.removeAttribute('src');   /* 断开流，防止无限重连 */
      }
    }, 4000);
  };
})();
'''
    open(J, "w", encoding="utf-8").write(js)
    print("摄像头保护已加")

# 进入人脸页时启动计时
if "__guardCam" not in js.split("/* 摄像头流保护")[0]:
    old = "    if (LAST_STEP !== 'face') img.src = img.dataset.src + '?t=' + Date.now();"
    new = ("    if (LAST_STEP !== 'face') {\n"
           "      img.src = img.dataset.src + '?t=' + Date.now();\n"
           "      if (window.__guardCam) window.__guardCam();\n"
           "    }")
    if old in js:
        js = js.replace(old, new, 1)
        open(J, "w", encoding="utf-8").write(js)
        print("人脸页已接入计时")
