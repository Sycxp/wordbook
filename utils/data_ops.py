# -*- coding: utf-8 -*-
"""数据库与收藏数据操作辅助工具。"""

import os
import shutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils.database import DatabaseManager
    from utils.favorites import FavoritesManager


def backup_database(db_path: str, backup_dir: str, timestamp: str) -> str:
    """备份数据库文件，返回备份路径。"""
    if not os.path.exists(db_path):
        raise FileNotFoundError("数据库不存在，无法备份")

    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, f"wordbook_db_{timestamp}.db")
    shutil.copy2(db_path, backup_path)
    return backup_path


def delete_database(db_path: str) -> None:
    """删除数据库文件。"""
    if not os.path.exists(db_path):
        raise FileNotFoundError("数据库不存在")
    os.remove(db_path)


def check_database_status(db_path: str) -> str:
    """返回数据库状态描述文本。"""
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        return f"数据库：存在 ({size / 1024:.1f} KB)"
    return "数据库：不存在"


def rebuild_favorites_from_db(
    db_manager: "DatabaseManager",
    favorites_manager: "FavoritesManager",
) -> int:
    """从数据库读取全部单词并覆盖重建收藏文件，返回单词数。"""
    words = db_manager.get_all_words()
    return favorites_manager.rebuild_from_words(words)
