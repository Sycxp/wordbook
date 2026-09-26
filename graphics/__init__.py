# -*- coding: utf-8 -*-
"""
图形界面包。

包含主窗口、设置界面等 GUI 组件。
"""

from graphics.main_window import MainWindow
from graphics.settings import SettingsManager, get_settings_tab_widget

__all__ = ["MainWindow", "SettingsManager", "get_settings_tab_widget"]
