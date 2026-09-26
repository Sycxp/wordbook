# -*- coding: utf-8 -*-
"""
后台重建数据库工作线程模块。

根据给定的单词列表，逐个查询并保存到数据库，用于从收藏文件重建数据库。
"""

from loguru import logger
from PySide6.QtCore import QThread, Signal

from handle.query_handle import QueryHandler
from utils.database import DatabaseManager


class RebuildWorker(QThread):
    """
    重建工作线程类。

    信号：
        progress(int, int, str) : 当前进度（当前序号、总数、当前单词）
        finished(int, str)      : 完成时返回成功数量和消息
        error(str)              : 出错时返回错误信息
    """

    progress = Signal(int, int, str)
    finished = Signal(int, str)
    error = Signal(str)

    def __init__(self, words: list, db_path: str):
        """
        初始化重建线程。

        Args:
            words: 需要查询的单词列表。
            db_path: 数据库文件路径。
        """
        super().__init__()
        self.words = words
        self.db_path = db_path
        self.query_handler = QueryHandler()
        self.db_manager = DatabaseManager(db_path)

    def run(self):
        """执行重建任务，逐个查询并保存单词。"""
        logger.info(f"开始重建数据库，共 {len(self.words)} 个单词")
        try:
            total = len(self.words)
            success_count = 0

            for i, word in enumerate(self.words):
                self.progress.emit(i + 1, total, word)

                data = self.query_handler.query_word(word)

                # 仅当释义非空时保存
                if data and data.get("meanings"):
                    if self.db_manager.save_word(word, data):
                        success_count += 1
                        logger.debug(f"单词 '{word}' 保存成功")
                else:
                    logger.warning(f"单词 '{word}' 查询结果为空，跳过保存")

            self.finished.emit(success_count, f"重建完成，成功 {success_count}/{total} 个单词")
            logger.info(f"数据库重建完成：成功 {success_count}/{total} 个单词")

        except Exception as e:
            logger.error(f"重建线程异常：{e}")
            self.error.emit(str(e))
