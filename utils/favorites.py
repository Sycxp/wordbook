# -*- coding: utf-8 -*-
"""收藏文件管理。"""

import os
import shutil
from typing import List, Tuple


class FavoritesManager:
    """封装收藏文件的读写、备份、导入、重建等操作。"""

    def __init__(self, favorites_path: str):
        self.favorites_path = favorites_path

    def exists(self) -> bool:
        """收藏文件是否存在。"""
        return os.path.exists(self.favorites_path)

    def load(self) -> List[str]:
        """读取收藏单词列表，自动忽略空行。"""
        if not self.exists():
            return []
        with open(self.favorites_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    def count(self) -> int:
        """收藏单词数量。"""
        return len(self.load())

    def _save(self, words: List[str]) -> None:
        """覆盖写入收藏单词列表。"""
        parent = os.path.dirname(self.favorites_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(self.favorites_path, "w", encoding="utf-8") as f:
            for word in words:
                f.write(f"{word}\n")

    def add(self, word: str) -> Tuple[bool, str]:
        """
        添加单词到收藏。

        Returns:
            (是否成功, 提示消息)
        """
        if not word:
            return False, "无效单词"

        words = self.load()
        if word in words:
            return False, "该单词已在收藏列表中"

        parent = os.path.dirname(self.favorites_path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(self.favorites_path, "a", encoding="utf-8") as f:
            f.write(f"{word}\n")
        return True, "已添加到收藏列表"

    def delete(self, word: str) -> bool:
        """从收藏中删除指定单词。返回是否实际删除。"""
        words = self.load()
        new_words = [w for w in words if w != word]
        if len(new_words) == len(words):
            return False
        self._save(new_words)
        return True

    def delete_file(self) -> None:
        """删除收藏文件。"""
        if self.exists():
            os.remove(self.favorites_path)

    def backup(self, backup_dir: str, timestamp: str) -> str:
        """备份收藏文件，返回备份路径。"""
        if not self.exists():
            raise FileNotFoundError("收藏文件不存在，无法备份")

        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, f"wordbook_fav_{timestamp}.txt")
        shutil.copy2(self.favorites_path, backup_path)
        return backup_path

    def import_from_file(self, file_path: str) -> Tuple[int, int]:
        """
        从外部文本文件导入单词，与现有收藏去重合并。

        Returns:
            (导入文件中的单词数, 合并后总单词数)
        """
        with open(file_path, "r", encoding="utf-8") as f:
            words = [line.strip() for line in f if line.strip()]

        existing = self.load()
        merged = sorted(set(existing + words))
        self._save(merged)
        return len(words), len(merged)

    def rebuild_from_words(self, words: List[str]) -> int:
        """用给定单词列表覆盖重建收藏文件，返回写入数量。"""
        self._save(words)
        return len(words)

    def get_status(self) -> str:
        """返回收藏状态描述文本。"""
        if not self.exists():
            return "收藏：不存在"
        return f"收藏：存在 ({self.count()} 个单词)"
