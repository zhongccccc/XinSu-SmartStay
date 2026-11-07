# -*- coding: utf-8 -*-
"""自动找端口 + 模拟模式下 issue 直接失败（不许假装成功）"""
P = r"E:\zhikong\app\backend\devices\lock.py"
s = open(P, encoding="utf-8").read()

OLD = """    def issue(self, room, guest, code, card_uid, ttl_min):
        if self._use_mock:
            return self._mock.issue(room, guest, code, card_uid, ttl_min)"""

NEW = """    def issue(self, room, guest, code, card_uid, ttl_min):
        if self._use_mock:
            # 板子没连上：直接报错，绝不能让界面以为下发成功
            return False, "门锁板未连接（请检查门锁板供电/USB）"
"""

if OLD in s and "门锁板未连接" not in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("[lock] mock 模式下 issue 改为返回失败")
else:
    print("状态:", "已存在" if "门锁板未连接" in s else "未匹配")
