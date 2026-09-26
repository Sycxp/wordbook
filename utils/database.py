# -*- coding: utf-8 -*-
"""
数据库管理模块。

提供对 SQLite 数据库的增删改查操作，专门用于存储单词及其音标、释义信息。
支持单词的保存、查询、随机获取及获取全部单词列表。
"""

import os
import sqlite3
from typing import Any, Dict, Optional

from loguru import logger


class DatabaseManager:
    """数据库管理器，封装 SQLite 操作。"""

    def __init__(self, db_path: str = "data/wordbook.db"):
        """
        初始化数据库管理器，确保目录存在并创建表结构。

        Args:
            db_path: 数据库文件路径。
        """
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self.db_path = db_path
        self.init_db()
        self.check_table()
        logger.info(f"数据库初始化完成：{db_path}")

    def init_db(self) -> None:
        """创建 words 表（如果不存在）。"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE NOT NULL,
                uk_pron TEXT,
                us_pron TEXT,
                meanings TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def check_table(self) -> bool:
        """
        检查 words 表是否存在，若不存在则调用 init_db 创建。

        Returns:
            表存在返回 True，否则（重建后）返回 False。
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='words'
            """)
            result = cursor.fetchone()
            conn.close()

            if not result:
                logger.warning("表 words 不存在，正在重建...")
                self.init_db()
                return False
            return True
        except Exception as e:
            logger.error(f"检查表失败：{e}")
            self.init_db()
            return False

    def save_word(self, word: str, data: Dict[str, Any]) -> bool:
        """
        保存或更新单词记录。

        若释义为空，则跳过保存并返回 False。

        Args:
            word: 单词字符串。
            data: 包含 uk_pron, us_pron, meanings 的字典。

        Returns:
            保存成功返回 True，否则 False。
        """
        try:
            meanings = data.get("meanings", [])
            if not meanings or (isinstance(meanings, list) and len(meanings) == 0):
                logger.warning(f"单词 '{word}' 释义为空，跳过保存")
                return False

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # 将释义列表转换为分隔字符串存储
            meanings_str = ";  ".join([f"{p}: {d}" for p, d in meanings])

            cursor.execute(
                """
                INSERT INTO words (word, uk_pron, us_pron, meanings)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(word) DO UPDATE SET
                    uk_pron=excluded.uk_pron,
                    us_pron=excluded.us_pron,
                    meanings=excluded.meanings
            """,
                (word, data.get("uk_pron"), data.get("us_pron"), meanings_str),
            )
            conn.commit()
            conn.close()
            logger.debug(f"单词 '{word}' 已保存到数据库")
            return True
        except Exception as e:
            logger.error(f"保存单词失败：{e}")
            return False

    def get_word(self, word: str) -> Optional[Dict[str, Any]]:
        """
        根据单词查询记录。

        Args:
            word: 要查询的单词。

        Returns:
            若找到则返回包含 word, uk_pron, us_pron, meanings（列表）的字典，
            否则返回 None。
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM words WHERE word = ?", (word,))
            row = cursor.fetchone()
            conn.close()

            if row:
                data = dict(row)
                meanings_str = data.get("meanings", "")
                meanings = []
                if meanings_str:
                    # 与 get_random_word 保持一致的解析方式
                    entries = meanings_str.split(";  ")
                    for entry in entries:
                        if ": " in entry:
                            pos, defn = entry.split(": ", 1)
                            meanings.append((pos.strip(), defn.strip()))
                data["meanings"] = meanings
                return data
            return None
        except Exception as e:
            logger.error(f"查询数据库失败：{e}")
            return None

    def get_random_word(self) -> Optional[Dict[str, Any]]:
        """
        从数据库中随机获取一个单词。

        Returns:
            单词数据字典，若无记录则返回 None。
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM words ORDER BY RANDOM() LIMIT 1")
            row = cursor.fetchone()
            conn.close()

            if row:
                data = dict(row)
                meanings_str = data.get("meanings", "")
                meanings = []
                if meanings_str:
                    entries = meanings_str.split(";  ")
                    for entry in entries:
                        if ": " in entry:
                            pos, defn = entry.split(": ", 1)
                            meanings.append((pos.strip(), defn.strip()))
                data["meanings"] = meanings
                logger.debug(f"随机获取单词：{data.get('word', '未知')}")
                return data
            return None
        except Exception as e:
            logger.error(f"随机查询单词失败：{e}")
            return None

    def get_all_words(self) -> list:
        """
        获取数据库中所有单词（按字母顺序）。

        Returns:
            单词字符串列表。
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT word FROM words ORDER BY word")
            rows = cursor.fetchall()
            conn.close()
            return [row[0] for row in rows]
        except Exception as e:
            logger.error(f"获取所有单词失败：{e}")
            return []

    def merge_from_db(self, source_db_path: str) -> tuple[int, int]:
        """
        从另一个 SQLite 数据库合并单词记录。

        源数据库需包含 words 表，字段与当前数据库一致。
        冲突时以源数据库内容覆盖当前数据库。

        Args:
            source_db_path: 源数据库文件路径。

        Returns:
            (合并处理的单词数, 源数据库总单词数)。
            若失败则返回 (0, 0)。
        """
        if not os.path.exists(source_db_path):
            logger.error(f"源数据库不存在：{source_db_path}")
            return 0, 0

        try:
            src_conn = sqlite3.connect(source_db_path)
            src_conn.row_factory = sqlite3.Row
            src_cursor = src_conn.cursor()
            # 检查 words 表是否存在
            src_cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='words'
            """)
            if not src_cursor.fetchone():
                logger.error(f"源数据库 {source_db_path} 中没有 words 表")
                src_conn.close()
                return 0, 0

            src_cursor.execute("SELECT word, uk_pron, us_pron, meanings FROM words")
            rows = src_cursor.fetchall()
            src_conn.close()

            if not rows:
                logger.info(f"源数据库 {source_db_path} 中无单词记录")
                return 0, 0

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            count = 0
            for row in rows:
                cursor.execute(
                    """
                    INSERT INTO words (word, uk_pron, us_pron, meanings)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(word) DO UPDATE SET
                        uk_pron=excluded.uk_pron,
                        us_pron=excluded.us_pron,
                        meanings=excluded.meanings
                    """,
                    (row["word"], row["uk_pron"], row["us_pron"], row["meanings"]),
                )
                count += 1
            conn.commit()
            conn.close()
            logger.info(f"从 {source_db_path} 合并了 {count} 个单词")
            return count, len(rows)
        except Exception as e:
            logger.error(f"合并数据库失败：{e}")
            return 0, 0
