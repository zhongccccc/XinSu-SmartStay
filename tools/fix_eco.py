# -*- coding: utf-8 -*-
"""退房时把房间切到节能模式。"""
P = r"E:\zhikong\app\backend\core\model.py"
s = open(P, encoding="utf-8").read()

OLD = """            except Exception as e:
                self.db.audit("error", {"where": "checkout", "err": str(e)})
        # 关掉该房间的在住订单"""
NEW = """            except Exception as e:
                self.db.audit("error", {"where": "checkout", "err": str(e)})
        # 房间节能复位：灯、风扇全关
        self.apply_room_mode("eco", room)
        # 关掉该房间的在住订单"""

if "房间节能复位" not in s and OLD in s:
    s = s.replace(OLD, NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("退房节能复位已插入")
else:
    print("状态:", "已存在" if "房间节能复位" in s else "未匹配")
