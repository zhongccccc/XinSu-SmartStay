# -*- coding: utf-8 -*-
"""把 build_lock 也接到端口认领结果上。"""
P = r"E:\zhikong\app\backend\main.py"
s = open(P, encoding="utf-8").read()

OLD = '''        self.lock = build_lock(CONF["devices"], self.db, log,
                               on_event=self._on_lock_event)'''
NEW = '''        _ports = discover_serial_ports(log)
        _dev = dict(CONF["devices"])
        _dev["lock"] = dict(_dev.get("lock") or {})
        if _ports.get("lock"):
            _dev["lock"]["port"] = _ports["lock"]
        _home_port = _ports.get("home") or _dev.get("home_port")
        self.lock = build_lock(_dev, self.db, log,
                               on_event=self._on_lock_event)'''

if "_ports = discover_serial_ports(log)" not in s and OLD in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("门锁板端口认领已接入")
else:
    print("状态:", "已存在" if "_ports = discover_serial_ports" in s else "未匹配")
