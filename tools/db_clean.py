import sqlite3
p = "/opt/zhikong/data/zhikong.db"
c = sqlite3.connect(p)
c.execute("DELETE FROM orders")
c.execute("DELETE FROM workorders")
c.commit()
n = c.execute("SELECT COUNT(*) FROM audit").fetchone()[0]
print("orders/workorders cleared; audit rows kept:", n)
c.close()
