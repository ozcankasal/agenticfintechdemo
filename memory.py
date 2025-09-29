import sqlite3, time
from typing import Optional, List, Tuple
from pathlib import Path

class ShortTermMemory:
    def __init__(self):
        self._store = {}
    def get(self, key, default=None):
        return self._store.get(key, default)
    def set(self, key, value):
        self._store[key] = value
    def as_dict(self):
        return dict(self._store)

class LongTermMemory:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT,
                    content TEXT NOT NULL,
                    created_at REAL
                )
            """)
            conn.commit()

    def save(self, topic: str, content: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO memory(topic, content, created_at) VALUES(?,?,?)",
                (topic, content, time.time())
            )
            conn.commit()

    def recall(self, topic: Optional[str]=None, limit: int=5) -> List[Tuple[int,str,str,float]]:
        with sqlite3.connect(self.db_path) as conn:
            if topic:
                rows = conn.execute(
                    "SELECT id, topic, content, created_at FROM memory WHERE topic=? ORDER BY id DESC LIMIT ?",
                    (topic, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, topic, content, created_at FROM memory ORDER BY id DESC LIMIT ?",
                    (limit,)
                ).fetchall()
        return rows