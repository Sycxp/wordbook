# -*- coding: utf-8 -*-
"""
WordBook 应用程序主入口模块。

负责初始化应用环境、加载配置、应用主题、设置图标，并启动主窗口。
在打包（PyInstaller）与开发环境之间进行路径隔离，确保资源与数据目录正确。
"""

import os
import sys

from loguru import logger
from PySide6.QtGui import QGuiApplication, QIcon, Qt
from PySide6.QtWidgets import QApplication

from graphics.main_window import MainWindow
from utils.load_settings import read_settings

# ==================== 路径环境初始化 ====================
if getattr(sys, "frozen", False):
    # PyInstaller 打包后：可执行文件所在目录作为数据根目录
    EXE_ROOT = os.path.dirname(sys.executable)
    # 资源文件位于临时解包目录（_MEIPASS），只读
    RESOURCE_ROOT = sys._MEIPASS if hasattr(sys, "_MEIPASS") else EXE_ROOT
    DATA_ROOT = EXE_ROOT
else:
    # 开发环境：以当前脚本所在目录为项目根
    EXE_ROOT = os.path.dirname(os.path.abspath(__file__))
    RESOURCE_ROOT = EXE_ROOT
    DATA_ROOT = os.path.join(EXE_ROOT, "data")

# 确保数据子目录存在
os.makedirs(os.path.join(DATA_ROOT, "logs"), exist_ok=True)
os.makedirs(os.path.join(DATA_ROOT, "backup"), exist_ok=True)
os.makedirs(os.path.join(DATA_ROOT, "user"), exist_ok=True)

# 将路径信息注入环境变量，供其他模块使用
os.environ["WORDBOOK_DATA_ROOT"] = DATA_ROOT
os.environ["WORDBOOK_RESOURCE_ROOT"] = RESOURCE_ROOT


def load_qss_theme(theme_name: str, font_size: int) -> str:
    """
    根据主题名称和字体大小加载对应的 QSS 样式表。

    支持三种主题：深色模式、浅色模式、跟随系统。
    当跟随系统时，通过 QGuiApplication.styleHints() 动态判断当前系统配色。

    Args:
        theme_name: 主题名称（"深色模式" / "浅色模式" / "跟随系统"）
        font_size: 基础字体大小（像素），将替换样式表中的 {font_size} 占位符

    Returns:
        加载成功的 QSS 字符串，若失败则返回空字符串。
    """
    if theme_name == "深色模式":
        qss_file = "dark.qss"
    elif theme_name == "浅色模式":
        qss_file = "light.qss"
    else:  # 跟随系统
        qss_file = "dark.qss" if QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark else "light.qss"

    qss_path = os.path.join(RESOURCE_ROOT, "resources", "styles", qss_file)

    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            qss_content = f.read()
        qss_content = qss_content.replace("{font_size}", str(font_size))
        logger.success(f"主题加载成功：{qss_file}")
        return qss_content
    except FileNotFoundError:
        logger.error(f"主题文件不存在：{qss_path}")
        return ""
    except Exception as e:
        logger.error(f"加载主题失败：{e}")
        return ""


def main() -> int:
    """
    应用程序主函数。

    完成日志配置、QApplication 实例创建、设置加载、主题应用、图标设置，
    最后显示主窗口并进入事件循环。

    Returns:
        应用程序退出码。
    """
    # ---------- 日志配置 ----------
    logger.remove()
    logger.add(
        os.path.join(DATA_ROOT, "logs", "wordbook_{time:YYYY-MM-DD}.log"),
        rotation="1 day",
        retention="7 days",
        level="DEBUG",
        encoding="utf-8",
    )
    logger.add(sys.stderr, level="INFO")

    logger.info("WordBook 正在启动...")
    logger.info(f"EXE_ROOT: {EXE_ROOT}")
    logger.info(f"DATA_ROOT: {DATA_ROOT}")
    logger.info(f"RESOURCE_ROOT: {RESOURCE_ROOT}")

    # ---------- 创建应用实例 ----------
    app = QApplication(sys.argv)

    # ---------- 加载用户设置 ----------
    settings = read_settings()
    general = settings.get("general", {})
    theme = general.get("theme", "跟随系统")
    font_size = int(general.get("font_size", "12"))

    # ---------- 应用主题 ----------
    qss = load_qss_theme(theme, font_size)
    if qss:
        app.setStyleSheet(qss)
        logger.info(f"已应用主题：{theme}, 字体：{font_size}px")

    # ---------- 设置应用元信息 ----------
    app.setApplicationName("WordBook")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("MiaoBu")

    # ---------- 设置窗口图标 ----------
    icon_path = os.path.join(RESOURCE_ROOT, "resources", "icons", "app_icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        logger.info(f"已设置窗口图标：{icon_path}")
    else:
        logger.warning(f"图标文件未找到：{icon_path}")

    # ---------- 创建并显示主窗口 ----------
    window = MainWindow()
    logger.info("主窗口创建成功，正在显示...")
    window.show()

    return app.exec()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.exception(f"程序发生未捕获的异常：{e}")
        sys.exit(1)
