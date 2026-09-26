# -*- coding: utf-8 -*-
"""
单词查询业务处理模块。

封装了单词查询和格式化功能，底层使用 IcibaParser 获取数据。
"""

from typing import Any, Dict, Optional

from loguru import logger

from utils.parser import IcibaParser


class QueryHandler:
    """单词查询处理器，负责调用解析器并格式化结果。"""

    def __init__(self):
        """初始化处理器，创建解析器实例。"""
        self.parser = IcibaParser()

    def query_word(self, word: str) -> Optional[Dict[str, Any]]:
        """
        查询指定单词的释义数据。

        Args:
            word: 要查询的单词字符串

        Returns:
            单词数据字典（包含音标、释义等），若查询失败或单词为空则返回 None。
        """
        if not word.strip():
            logger.warning("查询单词为空，跳过")
            return None

        logger.info(f"查询单词：{word}")
        try:
            data = self.parser.fetch_word_data(word.strip())
            if data:
                logger.debug(f"单词 '{word}' 查询成功，数据 keys: {list(data.keys())}")
            else:
                logger.warning(f"单词 '{word}' 查询返回空数据")
            return data
        except Exception as e:
            logger.error(f"查询单词 '{word}' 时发生异常：{e}")
            return None

    def format_word_info(self, word: str, data: Dict[str, Any]) -> str:
        """
        将单词数据格式化为便于阅读的文本。

        Args:
            word: 单词本身
            data: 包含音标和释义的字典

        Returns:
            格式化后的多行文本字符串。
        """
        logger.debug(f"格式化单词信息：{word}")
        info = f"单词：{word}\n"
        if data.get("uk_pron"):
            info += f"英式音标：{data['uk_pron']}\n"
        if data.get("us_pron"):
            info += f"美式音标：{data['us_pron']}\n"
        info += "\n释义：\n"
        for pos, defn in data.get("meanings", []):
            info += f"{pos} {defn}\n"
        return info
