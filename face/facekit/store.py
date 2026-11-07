"""特征缓存与审计日志。

合规底线：不落人脸图，只落「加盐哈希 + 128 维特征 + 分数 + 时间戳」。
特征同样属于生物识别信息，库文件要设权限，并约定留存期。
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path

import numpy as np


def hash_id(id_number: str, salt: str) -> str:
    return hashlib.sha256((salt + id_number).encode("utf-8")).hexdigest()[:32]


class EmbeddingStore:
    def __init__(self, db_path: str | Path, salt: str = "change-me-per-site") -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.salt = salt
        self.conn = sqlite3.connect(str(db_path))
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS id_embedding (
                   id_hash    TEXT PRIMARY KEY,
                   embedding  BLOB NOT NULL,
                   dim        INTEGER NOT NULL,
                   created_at REAL NOT NULL,
                   updated_at REAL NOT NULL
               )"""
        )
        self.conn.commit()

    def get(self, id_number: str) -> np.ndarray | None:
        key = hash_id(id_number, self.salt)
        row = self.conn.execute(
            "SELECT embedding, dim FROM id_embedding WHERE id_hash = ?", (key,)
        ).fetchone()
        if row is None:
            return None
        return np.frombuffer(row[0], dtype=np.float32).reshape(row[1])

    def put(self, id_number: str, embedding: np.ndarray) -> None:
        key = hash_id(id_number, self.salt)
        vec = np.asarray(embedding, np.float32).ravel()
        now = time.time()
        self.conn.execute(
            """INSERT INTO id_embedding (id_hash, embedding, dim, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(id_hash) DO UPDATE SET
                   embedding = excluded.embedding,
                   dim = excluded.dim,
                   updated_at = excluded.updated_at""",
            (key, vec.tobytes(), int(vec.size), now, now),
        )
        self.conn.commit()

    def delete(self, id_number: str) -> None:
        self.conn.execute(
            "DELETE FROM id_embedding WHERE id_hash = ?", (hash_id(id_number, self.salt),)
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()


class AuditLog:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, record: dict) -> None:
        record = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), **record}
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
