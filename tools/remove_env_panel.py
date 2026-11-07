# -*- coding: utf-8 -*-
"""从客人界面移除客房环境面板；完成页加"房间已准备"提示。"""
import re

P = r"E:\zhikong\app\web\index.html"
s = open(P, encoding="utf-8").read()

# 1) 删掉客房环境面板
s2, n1 = re.subn(r'\s*<!-- 客房环境（来自智能家居板） -->.*?</div>\s*</div>\s*</div>\s*</div>', '', s, flags=re.S)
if n1 == 0:
    # 退一步：按起止注释/结构删
    start = s.find('<div class="env-panel" id="homeEnv">')
    if start > 0:
        # 找到匹配的结束（env-panel 后跟着 chat）
        end = s.find('<div class="chat" id="chat">', start)
        if end > 0:
            s2 = s[:start] + s[end:]
            n1 = 1
if n1:
    s = s2
    print("环境面板已移除")

# 2) 删掉顶栏胶囊
s = re.sub(r'\s*<div class="envchip" id="envChip">[^<]*</div>', '', s)
print("顶栏胶囊已移除" if 'envChip' not in s else "胶囊仍在")

# 3) 完成页加"房间已准备"提示
if 'id="roomReady"' not in s:
    s = s.replace('<div class="done-hint">首次开门请先在门锁上刷这张房卡完成绑定</div>',
                  '<div class="done-hint" id="roomReady">房间已为您开启灯光与通风</div>\n'
                  '        <div class="done-hint" id="cardBind">首次开门请先在门锁上刷这张房卡完成绑定</div>', 1)
    # 两条提示叠在一起会重叠，改成第二条上移
    print("完成页提示已加")

open(P, "w", encoding="utf-8").write(s)

C = r"E:\zhikong\app\web\style.css"
cs = open(C, encoding="utf-8").read()
cs = cs.replace(".env-panel{display:none}\n.envchip{display:none}", "/* 客房环境面板已从客人界面移除（改为流程自动联动） */")
cs = cs.replace("body.staff .env-panel{display:block}\nbody.staff .envchip{display:block}", "")
if "#cardBind" not in cs:
    cs += '''

/* 完成页两条提示上下排开 */
#roomReady{bottom:62px;color:#5fe0a8}
#cardBind{bottom:38px}
'''
    open(C, "w", encoding="utf-8").write(cs)
    print("CSS 已调整")

J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()
# 面板元素没了，bindHomeEnv 内部都是 $id 判断，安全；保留 toast 监听
open(J, "w", encoding="utf-8").write(js)
print("done")
