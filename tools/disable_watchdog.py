# -*- coding: utf-8 -*-
"""回到基线：去掉我加的看门狗（每 15 秒 ping 板子），恢复最初的通讯行为。"""
P = r"E:\zhikong\app\backend\devices\lock.py"
s = open(P, encoding="utf-8").read()

OLD = """        self._wd_stop = False
        threading.Thread(target=self._watchdog, daemon=True, name="lock-wd").start()"""
NEW = """        # 看门狗已停用：恢复最初的通讯行为（不周期 ping 板子）
        self._wd_stop = True"""

if OLD in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("看门狗已停用")
else:
    print("状态:", "已是停用" if "_wd_stop = True" in s else "未匹配")
