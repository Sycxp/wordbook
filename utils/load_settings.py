# -*- coding: utf-8 -*-
"""
设置加载与存储模块。

负责读取设置结构描述文件（JSON）以及用户设置数据文件（INI），
并提供读写接口。包含默认配置，在文件缺失时自动创建。
"""

import configparser
import json
import os
from typing import Any, Dict

from loguru import logger

# -------- 路径配置 --------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
DATA_ROOT = os.environ.get("WORDBOOK_DATA_ROOT", os.path.join(PROJECT_ROOT, "data"))
RESOURCE_ROOT = os.environ.get("WORDBOOK_RESOURCE_ROOT", PROJECT_ROOT)
STRUCT_PATH = os.path.join(RESOURCE_ROOT, "data", "graphics", "settings_struct.json")
DATA_PATH = os.path.join(DATA_ROOT, "user", "settings.ini")

# -------- 默认配置 --------
DEFAULT_SETTINGS = {
    "general": {"theme": "跟随系统", "font_size": "12"},
    "network": {"request_timeout": "10", "request_delay": "1"},
}


def load_settings_struct() -> Dict[str, Any]:
    """
    读取设置结构描述文件（JSON）。

    Returns:
        结构字典，若文件不存在或解析失败则返回空字典。
    """
    logger.debug("加载设置结构文件")
    if not os.path.exists(STRUCT_PATH):
        logger.warning(f"结构文件不存在：{STRUCT_PATH}")
        return {}

    try:
        with open(STRUCT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"读取结构文件失败：{e}")
        return {}


def read_settings() -> Dict[str, Dict[str, str]]:
    """
    读取用户设置数据文件（INI）。

    若文件不存在，则创建默认配置文件并返回默认配置。

    Returns:
        设置字典，格式为 {section: {key: value}}。
    """
    logger.debug("读取设置数据")
    config = configparser.ConfigParser()

    if not os.path.exists(DATA_PATH):
        logger.info("设置文件不存在，使用默认配置")
        _create_default_settings()
        return DEFAULT_SETTINGS

    try:
        config.read(DATA_PATH, encoding="utf-8")
        logger.success("设置数据加载成功")
        return {section: dict(config[section]) for section in config.sections()}
    except Exception as e:
        logger.error(f"读取设置失败：{e}")
        return DEFAULT_SETTINGS


def save_settings(data: Dict[str, Dict[str, Any]]) -> bool:
    """
    保存设置数据到文件（INI）。

    Args:
        data: 设置字典，键为 section，值为键值对。

    Returns:
        成功返回 True，否则 False。
    """
    logger.info("保存设置数据")
    try:
        config = configparser.ConfigParser()
        for section, items in data.items():
            config[section] = {k: str(v) for k, v in items.items()}

        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            config.write(f)

        logger.success("设置数据保存成功")
        return True
    except Exception as e:
        logger.error(f"保存设置失败：{e}")
        return False


def _create_default_settings() -> None:
    """创建默认配置文件（若目录不存在则自动创建）。"""
    try:
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        save_settings(DEFAULT_SETTINGS)
        logger.info(f"已创建默认配置文件：{DATA_PATH}")
    except Exception as e:
        logger.error(f"创建默认配置失败：{e}")


def get_setting(section: str, key: str, default: str = "") -> str:
    """
    安全获取单个设置项。

    Args:
        section: 配置段名称。
        key: 配置键名。
        default: 若未找到则返回的默认值。

    Returns:
        配置值（字符串），若未找到则返回 default。
    """
    settings = read_settings()
    return settings.get(section, {}).get(key, default)
