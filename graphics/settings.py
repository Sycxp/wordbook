# -*- coding: utf-8 -*-
"""
设置管理模块。

提供动态生成的设置界面，支持从结构描述文件加载配置项，
并保存用户偏好到 .ini 文件。包含主题、网络超时等常用设置。
"""

import os
import sys

from loguru import logger
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGroupBox,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from utils.load_settings import (
    load_settings_struct,
    read_settings,
    save_settings,
)

# 确保项目根目录在 sys.path 中，以便导入 utils
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.append(project_root)


class SettingsManager(QWidget):
    """
    设置管理器界面类。

    根据 settings_struct.json 中的结构动态生成输入控件，
    并管理用户数据的读取与保存。
    """

    def __init__(self, parent=None):
        """
        初始化设置管理器。

        Args:
            parent: 父窗口组件。
        """
        super().__init__(parent)
        self.structure = {}
        self.data = {}
        self.widgets_map = {}
        self.section_map = {}
        self.load()
        self._build_ui()
        logger.debug("设置管理器初始化完成")

    def load(self):
        """加载设置结构描述和当前数据。若结构或文件不存在，使用默认值。"""
        logger.debug("加载设置管理器的结构和数据")
        self.structure = load_settings_struct()
        self.data = read_settings()  # 文件不存在时返回默认值

    def _build_ui(self):
        """
        根据结构描述构建界面。

        遍历 settings 列表，为每个配置项创建对应的输入控件（QLineEdit 或 QComboBox），
        并放入 QGroupBox 中，最后添加保存按钮。
        """
        if not self.structure:
            self.load()

        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        settings_list = self.structure.get("settings", [])

        # 如果结构为空，使用默认配置（保证界面可用）
        if not settings_list:
            settings_list = [
                {
                    "section": "general",
                    "key": "theme",
                    "label": "界面主题",
                    "type": "combobox",
                    "options": ["浅色模式", "深色模式", "跟随系统"],
                    "default": "跟随系统",
                },
                {
                    "section": "general",
                    "key": "font_size",
                    "label": "字体大小",
                    "type": "input",
                    "default": "12",
                    "placeholder": "输入字体大小...",
                },
                {
                    "section": "network",
                    "key": "request_timeout",
                    "label": "网络请求超时阈值 (秒)",
                    "type": "input",
                    "default": "10",
                    "placeholder": "输入秒数...",
                },
                {
                    "section": "network",
                    "key": "request_delay",
                    "label": "网络请求最小间隔 (秒)",
                    "type": "input",
                    "default": "1",
                    "placeholder": "输入秒数...",
                },
            ]

        for item in settings_list:
            section = item.get("section", "general")
            key = item.get("key")
            label = item.get("label", key)
            type_ = item.get("type", "input")

            current_value = self.data.get(section, {}).get(key, item.get("default", ""))

            group = QGroupBox(label)
            group_layout = QVBoxLayout()
            widget = None

            if type_ == "input":
                widget = QLineEdit()
                widget.setText(str(current_value))
                widget.setPlaceholderText(item.get("placeholder", ""))
            elif type_ == "combobox":
                widget = QComboBox()
                options = item.get("options", [])
                widget.addItems(options)
                if current_value in options:
                    widget.setCurrentText(current_value)

            if widget:
                self.widgets_map[key] = widget
                self.section_map[key] = section
                group_layout.addWidget(widget)
                group.setLayout(group_layout)
                scroll_layout.addWidget(group)

        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.on_save)
        scroll_layout.addWidget(save_btn)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        self.setLayout(layout)

    def on_save(self):
        """
        保存按钮的槽函数。

        收集所有控件中的当前值，合并到现有配置中，写入 .ini 文件。
        保存成功后提示用户重启以应用字体/主题等设置。
        """
        logger.info("用户触发保存设置")
        new_data = {}
        for key, widget in self.widgets_map.items():
            section = self.section_map.get(key, "general")
            if section not in new_data:
                new_data[section] = {}

            if isinstance(widget, QLineEdit):
                new_data[section][key] = widget.text()
            elif isinstance(widget, QComboBox):
                new_data[section][key] = widget.currentText()

        # 合并到现有数据（保留未在界面中显示的配置项）
        current_data = read_settings()
        for sec, items in new_data.items():
            if sec not in current_data:
                current_data[sec] = {}
            current_data[sec].update(items)

        if save_settings(current_data):
            logger.info("设置保存成功")
            # 提示用户重启
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("成功")
            msg_box.setText("设置已保存至配置文件中。")
            msg_box.setInformativeText("字体和主题设置需要重启程序才能生效，是否立即重启？")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)

            ret = msg_box.exec()

            if ret == QMessageBox.StandardButton.Yes:
                logger.info("用户选择立即重启程序")
                try:
                    os.execl(sys.executable, *sys.argv)
                except Exception as e:
                    logger.error(f"重启失败：{e}")
                    QApplication.instance().quit()
            else:
                logger.info("用户选择稍后重启")
        else:
            logger.error("设置保存失败")
            QMessageBox.critical(self, "失败", "保存设置失败，请检查文件权限。")


def get_settings_tab_widget(parent=None):
    """
    工厂函数，返回设置页的 Widget 实例。

    Args:
        parent: 父组件。

    Returns:
        SettingsManager 实s例（继承自 QWidget）。
    """
    logger.debug("创建设置页面 Widget")
    return SettingsManager(parent)
