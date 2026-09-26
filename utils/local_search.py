# -*- coding: utf-8 -*-
"""本地检索辅助工具。"""

import difflib
from typing import List, Optional, Tuple


def search_words(all_words: List[str], text: str) -> Tuple[List[str], Optional[str]]:
    """
    根据检索词执行本地检索。

    规则：
        - 以 '-' 开头：子串匹配（不区分大小写）
        - 以 '?' 开头：模糊匹配

    Returns:
        (matches, error_message)
        error_message 为 None 表示检索成功；否则为提示信息。
    """
    if not text:
        return [], "请输入检索词"

    if not all_words:
        return [], "数据库中没有单词"

    if text.startswith("-"):
        keyword = text[1:].lower()
        if not keyword:
            return [], "请输入子串"
        matches = [w for w in all_words if keyword in w.lower()]
    elif text.startswith("?"):
        query = text[1:]
        if not query:
            return [], "请输入模糊检索词"
        matches = difflib.get_close_matches(query, all_words, n=20, cutoff=0.5)
    else:
        return [], "检索词需以 - 或 ? 开头\n- 表示子串匹配\n? 表示模糊匹配"

    return matches, None
