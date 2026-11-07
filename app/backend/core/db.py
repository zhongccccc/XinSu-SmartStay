# -*- coding: utf-8 -*-
"""SQLite 存储：入住订单 / 工单 / 门锁与设备事件审计。"""
import json
import os
import sqlite3
import threading
import time

from ..config import DATA_DIR


class DB:
    def __init__(self, path=None):
        self.path = path or os.path.join(DATA_DIR, "zhikong.db")
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init()

    def _init(self):
        with self._lock:
            c = self._conn
            c.executescript(
                """
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS orders(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guest TEXT, idno TEXT, room TEXT, price INTEGER,
                    card_uid TEXT, lock_code TEXT, checkin_at REAL, checkout_at REAL,
                    status TEXT DEFAULT 'inhouse', payload TEXT);
                CREATE TABLE IF NOT EXISTS workorders(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room TEXT, text TEXT, kind TEXT,
                    status TEXT DEFAULT 'created', created_at REAL);
                CREATE TABLE IF NOT EXISTS audit(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts REAL, kind TEXT, payload TEXT);
                CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit(ts);
                """
            )
            c.commit()

    # ---------- 订单 ----------
    def create_order(self, guest, idno, room, price, card_uid, lock_code, payload=None):
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO orders(guest,idno,room,price,card_uid,lock_code,checkin_at,status,payload)"
                " VALUES(?,?,?,?,?,?,?,?,?)",
                (guest, idno, room, price, card_uid, lock_code, time.time(), "inhouse",
                 json.dumps(payload or {}, ensure_ascii=False)))
            self._conn.commit()
            return cur.lastrowid

    def checkout(self, order_id):
        with self._lock:
            self._conn.execute("UPDATE orders SET status='checkedout', checkout_at=? WHERE id=?",
                               (time.time(), order_id))
            self._conn.commit()

    def set_order_card(self, order_id, uid):
        """把卡号写到订单上（门锁板首刷绑定时用）。"""
        cur = self._conn.cursor()
        cur.execute("UPDATE orders SET card_uid=? WHERE id=?", (uid, order_id))
        self._conn.commit()

    def inhouse_orders(self):
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM orders WHERE status='inhouse' ORDER BY id DESC LIMIT 50").fetchall()
        return [dict(r) for r in rows]

    # ---------- 工单 ----------
    def create_workorder(self, room, text, kind):
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO workorders(room,text,kind,created_at) VALUES(?,?,?,?)",
                (room, text, kind, time.time()))
            self._conn.commit()
            return cur.lastrowid

    def workorders(self, limit=20):
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM workorders ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]

    def next_workorder(self):
        """前台 App 取下一单（模拟派单队列）。"""
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM workorders WHERE status='created' ORDER BY id ASC LIMIT 1").fetchone()
        return dict(row) if row else None

    def set_workorder_status(self, wid, status):
        with self._lock:
            self._conn.execute("UPDATE workorders SET status=? WHERE id=?", (status, wid))
            self._conn.commit()

    # ---------- 审计 ----------
    def audit(self, kind, payload):
        with self._lock:
            self._conn.execute("INSERT INTO audit(ts,kind,payload) VALUES(?,?,?)",
                               (time.time(), kind, json.dumps(payload, ensure_ascii=False)))
            self._conn.commit()

    def recent_audit(self, limit=30):
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM audit ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            try:
                d["payload"] = json.loads(d["payload"])
            except Exception:
                pass
            out.append(d)
        return out
