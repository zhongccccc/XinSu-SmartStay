# -*- coding: utf-8 -*-
J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()

OLD = """  } else if (LAST_STEP === 'face') {
    const img = $('#camImg');
    img.removeAttribute('src');
  }"""
NEW = """  } else if (LAST_STEP === 'face') {
    window.__autoFaceOnce = false;      /* 下次进人脸页重新自动放行 */
    const img = $('#camImg');
    img.removeAttribute('src');
    const bf = $('#btnFace');
    if (bf) { bf.disabled = false; bf.textContent = '开始人脸核验'; }
  }"""

if "__autoFaceOnce = false;      /*" not in js and OLD in js:
    js = js.replace(OLD, NEW, 1)
    open(J, "w", encoding="utf-8").write(js)
    print("已加重置")
else:
    print("状态:", "已存在" if "__autoFaceOnce = false;      /*" in js else "未匹配")
