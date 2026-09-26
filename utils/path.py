# -*- coding: utf-8 -*-
"""路径与时间相关辅助工具。"""

import os
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DataPaths:
    """应用数据路径集合。"""

    project_root: str
    db_path: str
    favorites_path: str
    backup_dir: str
    help_path: str


def build_data_paths(project_root: str) -> DataPaths:
    """根据数据根目录构建各数据文件/目录路径。"""
    return DataPaths(
        project_root=project_root,
        db_path=os.path.join(project_root, "wordbook.db"),
        favorites_path=os.path.join(project_root, "user", "love.txt"),
        backup_dir=os.path.join(project_root, "backup"),
        help_path=os.path.join(project_root, "graphics", "help.md"),
    )


def get_timestamp() -> str:
    """返回当前时间戳字符串，用于备份文件名。"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")
