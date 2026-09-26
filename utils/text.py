# -*- coding: utf-8 -*-
"""文本格式化与解码辅助工具。"""

import base64
from typing import Any, Dict

from loguru import logger


def decode_base64(s: str) -> str:
    """解码 Base64 字符串为 UTF-8 文本，失败时返回错误提示。"""
    if not s:
        return ""
    try:
        return base64.b64decode(s).decode("utf-8")
    except Exception as e:
        logger.error(f"Base64 解码失败：{e}")
        return f"Base64 解码失败：{e}"


def format_word_info(data: Dict[str, Any]) -> str:
    """将单词数据字典格式化为界面展示文本。"""
    word = data.get("word", "未知")
    info = f"单词：{word}\n"
    if data.get("uk_pron"):
        info += f"英式音标：{data['uk_pron']}\n"
    if data.get("us_pron"):
        info += f"美式音标：{data['us_pron']}\n"
    info += "\n释义：\n"

    meanings = data.get("meanings", [])
    if isinstance(meanings, list):
        for pos, defn in meanings:
            info += f"{pos} {defn}\n"
    else:
        info += str(meanings)

    return info
