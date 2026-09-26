# -*- coding: utf-8 -*-
"""
网页解析模块（iciba 单词数据解析）。

负责请求 iciba 单词页面，解析 HTML 提取音标和释义信息，
并提供统一的查询接口。使用 BeautifulSoup 和 requests。
"""

import re
import time
from typing import Any, Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from utils.load_settings import get_setting


class IcibaParser:
    """iciba 单词解析器，提供单词数据获取与解析功能。"""

    BASE_URL = "https://www.iciba.com/word"

    def __init__(self) -> None:
        """
        初始化解析器，从配置中读取请求超时和延迟参数。
        """
        self.timeout = float(get_setting("network", "request_timeout", "10"))
        self.delay = float(get_setting("network", "request_delay", "1"))

        self.session = requests.Session()

        retry = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            backoff_factor=1.5,
            status_forcelist=(500, 502, 503, 504),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
                "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"),
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Referer": "https://www.iciba.com/",
                "Connection": "close",
            }
        )

        logger.debug(f"解析器初始化完成，超时：{self.timeout}s, 延迟：{self.delay}s")

    def fetch_word_data(self, word: str) -> Optional[Dict[str, Any]]:
        """
        从 iciba 获取单词完整数据（包含音标和释义）。

        Args:
            word: 要查询的单词。

        Returns:
            包含 'uk_pron', 'us_pron', 'meanings' 的字典，
            若失败则返回 None。
        """
        url = self.BASE_URL
        params = {"w": word}
        logger.info(f"正在查询单词：{word}")

        try:
            time.sleep(self.delay)

            logger.debug(f"请求 URL: {url}, 参数: {params}")
            response = self.session.get(
                url,
                params=params,
                timeout=(5, self.timeout),
            )

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After", "未知")
                logger.warning(f"触发 429，Retry-After={retry_after}")
                return None

            if response.status_code in (401, 403):
                logger.error(f"请求被拒绝，状态码：{response.status_code}，可能触发风控或需要更新会话")
                return None

            if response.status_code >= 500:
                logger.error(f"服务端错误，状态码：{response.status_code}")
                return None

            if response.status_code != 200:
                logger.error(f"请求失败，状态码：{response.status_code}")
                return None

            if self._is_blocked_page(response.text):
                logger.warning(f"单词 '{word}' 页面疑似风控/验证码")
                return None

            data = self.parse_word_data(response.text)
            if not data:
                logger.warning(f"单词 '{word}' 未解析到有效数据")
                return None

            logger.success(f"单词 '{word}' 查询成功")
            return data

        except requests.exceptions.Timeout as e:
            logger.error(f"请求超时：{e}")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"连接异常：{e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求异常：{e}")
            return None
        except Exception as e:
            logger.exception(f"解析错误：{e}")
            return None

    def parse_word_data(self, html_content: str) -> Optional[Dict[str, Any]]:
        """
        解析 HTML 内容，提取音标和释义。

        Args:
            html_content: 网页 HTML 字符串。

        Returns:
            包含音标和释义的字典，若释义为空仍会返回（meanings 为空列表）。
        """
        logger.debug("开始解析 HTML 内容")
        soup = BeautifulSoup(html_content, "html.parser")

        uk_pron, us_pron = self._parse_pronunciations(soup)
        meanings = self._parse_meanings(soup)

        if not uk_pron and not us_pron and not meanings:
            logger.warning("未解析到音标和释义，可能是风控页或页面结构变化")
            return None

        if not meanings:
            logger.warning("未找到释义内容")

        return {"uk_pron": uk_pron, "us_pron": us_pron, "meanings": meanings}

    def _parse_pronunciations(self, soup: BeautifulSoup) -> Tuple[Optional[str], Optional[str]]:
        """
        从 BeautifulSoup 对象中解析英式和美式音标。

        Args:
            soup: BeautifulSoup 对象。

        Returns:
            (uk_pron, us_pron) 元组，各自可能为 None。
        """
        uk_pron: Optional[str] = None
        us_pron: Optional[str] = None

        pronunciation_ul = soup.find("ul", class_=lambda c: c is not None and "Mean_symbols__" in c)
        if not pronunciation_ul:
            logger.debug("未找到音标元素")
            return uk_pron, us_pron

        for li in pronunciation_ul.find_all("li"):
            text = li.get_text()
            if "英" in text:
                match = re.search(r"\[.*?\]", text)
                if match:
                    uk_pron = match.group(0)
            elif "美" in text:
                match = re.search(r"\[.*?\]", text)
                if match:
                    us_pron = match.group(0)

        return uk_pron, us_pron

    def _parse_meanings(self, soup: BeautifulSoup) -> List[Tuple[str, str]]:
        """
        从 BeautifulSoup 对象中解析释义列表。

        Args:
            soup: BeautifulSoup 对象。

        Returns:
            释义列表，每个元素为 (词性, 释义字符串) 元组。
        """
        meanings: List[Tuple[str, str]] = []

        meaning_heading = None
        for h3 in soup.find_all("h3"):
            if "释义" in h3.get_text():
                meaning_heading = h3
                break

        if not meaning_heading:
            logger.debug("未找到释义标题")
            return meanings

        parent_div = meaning_heading.find_parent("div", class_=lambda c: c is not None and "Mean_normal__" in c)
        if not parent_div:
            logger.debug("未找到释义容器")
            return meanings

        ul = parent_div.find("ul", class_=lambda c: c is not None and "Mean_part__" in c)
        if not ul:
            logger.debug("未找到释义列表")
            return meanings

        for li in ul.find_all("li"):
            pos_tag = li.find("i")
            definition_div = li.find("div")

            if pos_tag is not None and definition_div is not None:
                pos = pos_tag.text.strip()
                definitions = []
                for span in definition_div.find_all("span"):
                    clean_text = re.sub(r"<!--.*?-->", "  ", span.text)
                    clean_text = clean_text.rstrip(";  ").strip()
                    if clean_text:
                        definitions.append(clean_text)

                full_definition = ";  ".join(definitions)
                meanings.append((pos, full_definition))

        return meanings

    def _is_blocked_page(self, html: str) -> bool:
        """
        检测页面是否疑似风控/验证码/访问受限页面。
        """
        lower_html = html.lower()
        keywords = (
            "验证码",
            "安全验证",
            "访问过于频繁",
            "人机验证",
            "captcha",
            "cf-chl",
            "cloudflare",
        )
        return any(keyword.lower() in lower_html for keyword in keywords)
