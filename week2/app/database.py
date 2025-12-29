"""
数据库操作层
封装所有数据库操作，提供清晰的接口和事务管理
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Generator
from loguru import logger


class Database:
    """数据库操作类，封装所有数据库相关操作"""
    
    def __init__(self, db_path: str | Path):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self._ensure_directory()
        self._init_schema()
    
    def _ensure_directory(self) -> None:
        """确保数据库目录存在"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        获取数据库连接的上下文管理器
        自动处理事务提交和回滚
        
        Yields:
            sqlite3.Connection: 数据库连接对象
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database transaction failed: {e}")
            raise
        finally:
            conn.close()
    
    def _init_schema(self) -> None:
        """初始化数据库表结构和索引"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建 notes 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)
            
            # 创建 action_items 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS action_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER,
                    text TEXT NOT NULL,
                    done INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (note_id) REFERENCES notes(id)
                )
            """)
            
            # 创建索引以优化查询性能
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_action_items_note_id 
                ON action_items(note_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_action_items_done 
                ON action_items(done)
            """)
            
            logger.info("Database schema initialized successfully")
    
    # ==================== Notes 操作 ====================
    
    def insert_note(self, content: str) -> int:
        """
        插入新笔记
        
        Args:
            content: 笔记内容
            
        Returns:
            int: 新插入笔记的 ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
            note_id = cursor.lastrowid
            logger.debug(f"Inserted note with id {note_id}")
            return note_id
    
    def get_note(self, note_id: int) -> Optional[dict]:
        """
        根据 ID 获取笔记
        
        Args:
            note_id: 笔记 ID
            
        Returns:
            Optional[dict]: 笔记数据字典，如果不存在返回 None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, content, created_at FROM notes WHERE id = ?",
                (note_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def list_notes(self) -> list[dict]:
        """
        获取所有笔记列表
        
        Returns:
            list[dict]: 笔记列表，按创建时间倒序排列
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, content, created_at FROM notes ORDER BY id DESC"
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    # ==================== Action Items 操作 ====================
    
    def insert_action_items(
        self, 
        items: list[str], 
        note_id: Optional[int] = None
    ) -> list[int]:
        """
        批量插入行动项
        
        Args:
            items: 行动项文本列表
            note_id: 关联的笔记 ID（可选）
            
        Returns:
            list[int]: 新插入的行动项 ID 列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            ids: list[int] = []
            for item in items:
                cursor.execute(
                    "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                    (note_id, item)
                )
                ids.append(cursor.lastrowid)
            logger.debug(f"Inserted {len(ids)} action items")
            return ids
    
    def get_action_item(self, item_id: int) -> Optional[dict]:
        """
        根据 ID 获取行动项
        
        Args:
            item_id: 行动项 ID
            
        Returns:
            Optional[dict]: 行动项数据字典，如果不存在返回 None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, note_id, text, done, created_at FROM action_items WHERE id = ?",
                (item_id,)
            )
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['done'] = bool(result['done'])  # 转换为布尔值
                return result
            return None
    
    def list_action_items(self, note_id: Optional[int] = None) -> list[dict]:
        """
        获取行动项列表
        
        Args:
            note_id: 如果指定，只返回该笔记关联的行动项
            
        Returns:
            list[dict]: 行动项列表，按创建时间倒序排列
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if note_id is None:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
                )
            else:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                    (note_id,)
                )
            rows = cursor.fetchall()
            results = []
            for row in rows:
                item = dict(row)
                item['done'] = bool(item['done'])  # 转换为布尔值
                results.append(item)
            return results
    
    def update_action_item_status(self, item_id: int, done: bool) -> bool:
        """
        更新行动项的完成状态
        
        Args:
            item_id: 行动项 ID
            done: 是否完成
            
        Returns:
            bool: 如果更新成功返回 True，如果行动项不存在返回 False
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE action_items SET done = ? WHERE id = ?",
                (1 if done else 0, item_id)
            )
            success = cursor.rowcount > 0
            if success:
                logger.debug(f"Updated action item {item_id} done status to {done}")
            else:
                logger.warning(f"Action item {item_id} not found")
            return success


