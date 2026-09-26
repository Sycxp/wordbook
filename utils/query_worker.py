# -*- coding: utf-8 -*-
"""
后台查询工作线程模块。

用于在非 UI 线程中执行单词查询任务，先查本地数据库，若无则访问网络，
并将结果通过信号传回主线程。
"""

from loguru import logger
from PySide6.QtCore import QThread, Signal

from utils.database import DatabaseManager
from utils.parser import IcibaParser


class QueryWorker(QThread):
    """
    查询工作线程类。

    信号：
        finished(dict) : 查询成功时携带单词数据字典
        error(str)     : 查询失败时携带错误信息
    """

    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, word: str):
        """
        初始化查询线程。

        Args:
            word: 要查询的单词字符串。
        """
        super().__init__()
        self.word = word
        self.parser = IcibaParser()
        self.db = DatabaseManager()

    def run(self):
        """线程运行入口，执行实际的查询逻辑。"""
        logger.debug(f"后台线程开始查询：{self.word}")
        try:
            # 1. 检查本地数据库
            local_data = self.db.get_word(self.word)
            if local_data:
                logger.info(f"单词 '{self.word}' 命中本地缓存")
                # 转换为与 parser 返回格式一致的数据
                data = {
                    "word": local_data["word"],
                    "uk_pron": local_data["uk_pron"],
                    "us_pron": local_data["us_pron"],
                    "meanings": local_data["meanings"],  # 已为列表格式
                }
                self.finished.emit(data)
                return

            # 2. 数据库无缓存，执行网络查询
            logger.debug(f"单词 '{self.word}' 未命中缓存，尝试网络查询")
            data = self.parser.fetch_word_data(self.word)
            if data:
                data["word"] = self.word  # 确保包含单词字段
                self.db.save_word(self.word, data)
                logger.info(f"单词 '{self.word}' 网络查询成功并已缓存")
                self.finished.emit(data)
            else:
                logger.warning(f"单词 '{self.word}' 网络查询失败")
                self.error.emit("网络查询失败")
        except Exception as e:
            logger.error(f"查询线程异常：{e}")
            self.error.emit(str(e))
