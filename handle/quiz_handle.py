# -*- coding: utf-8 -*-
"""
单词抽查业务处理模块。

提供两种模式：随机抽查（隐藏英文，显示中文释义，需用户输入英文）和随机选取（显示完整信息）。
支持从内存词池或直接数据库读取随机单词。
"""

import random
from typing import Any, Dict, List, Optional

from loguru import logger


class QuizHandler:
    """单词抽查处理器，管理当前单词、词池和模式状态。"""

    def __init__(self):
        """初始化处理器，清空词池和当前单词，默认处于抽查模式。"""
        self.word_pool: List[Dict[str, Any]] = []
        self.current_word: Optional[Dict[str, Any]] = None
        self.is_quiz_mode = True  # True=抽查模式（隐藏英文），False=选取模式（显示全部）

    def load_word_pool(self, words: List[Dict[str, Any]]) -> None:
        """
        加载单词池（用于内存模式）。

        Args:
            words: 单词数据字典列表。
        """
        self.word_pool = words.copy()
        logger.debug(f"加载单词池，共 {len(words)} 个单词")

    def get_random_word(self, hide_meaning: bool = True, db_manager=None) -> bool:
        """
        随机获取一个单词，并设置为当前单词。

        若提供 db_manager，则直接从数据库查询；否则从 word_pool 中随机选取。
        此方法不返回数据，调用方通过 get_quiz_info() 或 get_full_info() 获取显示内容。

        Args:
            hide_meaning: 是否隐藏英文（仅在非数据库模式下有效，数据库模式忽略此参数）
            db_manager: 数据库管理器实例（可选），若提供则优先使用

        Returns:
            成功获取返回 True，否则返回 False。
        """
        if db_manager:
            self.current_word = db_manager.get_random_word()
            logger.debug("从数据库获取随机单词")
        else:
            if not self.word_pool:
                logger.warning("单词池为空，无法获取随机单词")
                return False
            self.current_word = random.choice(self.word_pool)
            logger.debug("从内存词池获取随机单词")

        if self.current_word is None:
            logger.warning("获取随机单词失败（返回空）")
            return False

        logger.debug(f"当前单词：{self.current_word.get('word', '未知')}")
        return True

    def check_answer(self, user_answer: str) -> bool:
        """
        检查用户输入的英文是否与当前单词匹配（不区分大小写）。

        Args:
            user_answer: 用户输入的英文单词

        Returns:
            匹配返回 True，否则 False。
        """
        if not self.current_word:
            logger.warning("检查答案时当前单词为空")
            return False

        correct_word = self.current_word.get("word", "").strip().lower()
        user_ans = user_answer.strip().lower()
        result = user_ans == correct_word
        logger.debug(f"答案检查：用户输入 '{user_ans}'，正确 '{correct_word}'，结果 {result}")
        return result

    def get_full_info(self) -> str:
        """
        获取当前单词的完整信息（包括单词、音标、所有释义）。

        Returns:
            格式化的文本字符串，若无当前单词则返回空字符串。
        """
        if not self.current_word:
            return ""

        info = f"单词：{self.current_word.get('word', '')}\n"
        if self.current_word.get("uk_pron"):
            info += f"英式音标：{self.current_word['uk_pron']}\n"
        if self.current_word.get("us_pron"):
            info += f"美式音标：{self.current_word['us_pron']}\n"
        info += "\n释义：\n"
        for pos, defn in self.current_word.get("meanings", []):
            info += f"{pos} {defn}\n"
        return info

    def get_quiz_info(self) -> str:
        """
        获取抽查模式下的显示信息（隐藏英文，显示中文释义和音标）。

        提示用户根据释义输入英文。

        Returns:
            格式化的提示文本，若无当前单词则返回空字符串。
        """
        if not self.current_word:
            return ""

        info = "请根据以下释义写出英文单词：\n\n"
        info += "释义：\n"
        for pos, defn in self.current_word.get("meanings", []):
            info += f"{pos} {defn}\n"
        if self.current_word.get("uk_pron"):
            info += f"\n英式音标：{self.current_word['uk_pron']}"
        if self.current_word.get("us_pron"):
            info += f"\n美式音标：{self.current_word['us_pron']}"
        info += "\n\n输入英文单词后点击提交"
        return info
