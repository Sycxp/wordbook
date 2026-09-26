# -*- coding: utf-8 -*-
"""
WordBook 项目的安装配置文件（setuptools）。

支持 Python 3.8 及以上版本，兼容 PyInstaller 打包场景。
定义包结构、依赖、入口点及元数据，确保在开发环境和打包环境中均能正确安装。
"""

import sys
from pathlib import Path

# ---------- Python 版本检查 ----------
if sys.version_info < (3, 8):
    sys.exit("错误：WordBook 需要 Python 3.8 或更高版本（推荐 CPython 3.14.3）")

# ---------- 兼容性导入 ----------
try:
    from setuptools import find_packages, setup
except ImportError:
    from distutils.core import setup
    def find_packages(where=".", exclude=(), include=()):
        """
        简易包查找函数，供 distutils 回退使用。
        """
        return ["graphics", "utils", "handle"]


def read_requirements():
    """
    从 requirements.txt 中读取运行时依赖。

    过滤掉非必要的开发依赖（如 pyinstaller、pytest 等），仅保留运行时需要的包。
    返回依赖列表（含版本约束）。
    """
    req_path = Path(__file__).parent / "requirements.txt"
    if not req_path.exists():
        return []

    runtime_deps = {
        "PySide6",
        "loguru",
        "icecream",
        "requests",
        "beautifulsoup4",
        "bs4",
        "lxml",
        "soupsieve",
    }

    deps = []
    with open(req_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # 提取包名（忽略版本运算符）
            pkg_name = line.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip()
            if pkg_name in runtime_deps:
                deps.append(line)
    return deps


def read_readme():
    """读取项目根目录下的 README.md 文件内容，用作长描述。"""
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "WordBook - 信息学竞赛生的单词本工具"


def get_package_data():
    """
    定义非 Python 代码的资源文件（如 JSON 配置文件）。

    当前仅针对 graphics 和 utils 包收集相应的数据文件。
    """
    return {
        "graphics": ["*.json"],
        "utils": ["*.json"],
        "handle": [],
    }


# ---------- setup 主配置 ----------
setup(
    name="WordBook",
    version="0.1.2",
    description="单词本工具",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="喵布",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Education :: Language Learning",
    ],
    packages=find_packages(
        where=".",
        include=["graphics*", "utils*", "handle*"],
        exclude=["tests*", ".venv*", "__pycache__*", "*.tests*"],
    ),
    # 未指定 package_dir，默认从当前目录开始查找包
    entry_points={
        "console_scripts": [
            "wordbook=main:main",
        ],
    },
    install_requires=read_requirements(),
    extras_require={
        "dev": ["pyinstaller>=6.0.0", "pipreqs>=0.4.0", "ruff>=0.1.0"],
        "test": ["pytest>=7.0.0", "pytest-qt>=4.2.0"],
    },
    package_data=get_package_data(),
    include_package_data=True,
    keywords="wordbook vocabulary learning education pyside6",
    zip_safe=False,
)
