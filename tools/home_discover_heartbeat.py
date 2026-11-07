# -*- coding: utf-8 -*-
"""家居板发现：ping 不通时，只要收到心跳也算认领成功（shell 死了也能连上）。"""
P = r"E:\zhikong\app\backend\devices\home_board.py"
s = open(P, encoding="utf-8").read()

OLD = '''            if "ZH|ACK|PING" in text:
                m = re.search(r"ZH\\|ACK\\|PING\\|OK\\|([^|\\r\\n]+)", text)'''

NEW = '''            # ping 没回应时：看板子有没有在自发心跳（应用活着但 shell 挂了）
            if "ZH|ACK|PING" not in text:
                text += self._read(3.0)
            if "ZH|ACK|PING" in text or "[zh] alive" in text or "ZH|EVT|" in text:
                m = re.search(r"ZH\\|ACK\\|PING\\|OK\\|([^|\\r\\n]+)", text)'''

if OLD in s and "[zh] alive" not in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("已改为：心跳也算认领成功")
else:
    print("状态:", "已存在" if "[zh] alive" in s else "未匹配")
