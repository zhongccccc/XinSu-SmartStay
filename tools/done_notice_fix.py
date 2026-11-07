# -*- coding: utf-8 -*-
"""提醒块改成固定横幅（贴在顶部），不参与完成页的横向 flex 布局。"""
C = r"E:\zhikong\app\web\style.css"
cs = open(C, encoding="utf-8").read()

OLD = """.done-warn{
  width:100%;max-width:520px;margin:10px auto 6px;padding:10px 16px;
  border-radius:12px;text-align:center;
  background:linear-gradient(180deg,rgba(255,179,71,.16),rgba(255,179,71,.07));
  border:1px solid rgba(255,179,71,.55);
}"""
NEW = """.done-warn{
  position:fixed;left:50%;top:52px;transform:translateX(-50%);
  width:min(600px,94%);padding:8px 18px;z-index:6;
  border-radius:12px;text-align:center;
  background:linear-gradient(180deg,rgba(255,179,71,.18),rgba(255,179,71,.08));
  border:1px solid rgba(255,179,71,.6);
  box-shadow:0 6px 20px rgba(0,0,0,.35);
}"""

if OLD in cs:
    cs = cs.replace(OLD, NEW, 1)
    open(C, "w", encoding="utf-8").write(cs)
    print("已改为顶部固定横幅")
else:
    print("未匹配")
