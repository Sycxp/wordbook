# WordBook - 单词本

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.5%2B-green)](https://doc.qt.io/qtforpython/)
[![License](https://img.shields.io/badge/License-GPL--3.0--or--later-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)]()

WordBook 是一款面向学生的单词本工具，基于 PySide6 开发。它提供单词查询、收藏管理、随机抽查、本地检索以及数据备份与重建等功能，帮助您更高效地记忆和复习英文单词。

## 功能特性

- **单词查询**
  输入英文单词，联网查询音标与中文释义。查询结果自动保存到本地单词库，方便后续复习。

- **收藏管理**
  一键收藏重点单词，支持右键删除。收藏列表可备份、导入，也可从数据库重建。

- **单词抽查**
  - **随机抽查**：显示中文释义和音标，隐藏英文单词，您需要输入对应的英文。
  - **随机选取**：直接显示单词完整信息，适合快速浏览和记忆。

- **本地检索**
  在已查询过的单词中进行检索：
  - 以 `-` 开头：子串匹配，例如 `-tion` 查找包含 `tion` 的单词。
  - 以 `?` 开头：模糊匹配。

- **数据操作**
  - 数据库：备份、删除、导入、从收藏重建。
  - 收藏：备份、删除、从文件导入、从数据库重建。
  - 所有危险操作均有确认提示，并建议先备份。

- **个性化设置**
  - 界面主题：浅色模式 / 深色模式 / 跟随系统。
  - 字体大小调节。
  - 网络请求超时阈值与最小请求间隔。

- **多标签页界面**
  单词查询、单词抽查、设置、数据操作、关于、帮助，功能一目了然。

## 安装

### 方式一：下载安装包（推荐）

1. 前往 [Releases](https://github.com/yourname/WordBook/releases) 页面下载最新版 `WordBook_Setup.exe`。
2. 双击运行安装程序，按照提示完成安装。安装前会显示 GPL-3.0 许可协议，请阅读并接受。
3. 安装完成后，桌面和开始菜单会创建快捷方式。

### 方式二：从源码运行

适用于开发者或希望自行构建的用户。

```bash
# 克隆仓库
git clone https://github.com/yourname/WordBook.git
cd WordBook

# 创建虚拟环境（可选）
python -m venv .venv
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

> 要求 Python 3.8 或更高版本。Windows 平台推荐使用 Python 3.10+。

## 快速开始

1. 启动 WordBook，默认进入“单词查询”页面。
2. 在输入框中输入英文单词，点击“查询”或按回车。
3. 查询结果会显示音标和释义，并自动保存到本地。
4. 点击“收藏”按钮，把重点单词加入收藏列表。
5. 切换到“单词抽查”页面，选择“随机抽查”，点击“开始抽查”即可复习。
6. 定期到“数据操作”页面备份数据库和收藏，防止数据丢失。

## 使用说明

### 单词查询

- 输入单词后查询，右侧显示详细信息。
- 点击“收藏”将当前单词加入收藏列表。
- 左侧列表显示收藏的单词，点击可快速查询。
- 右键点击收藏单词可删除。
- 点击“本地检索”进入检索模式，支持 `-` 子串和 `?` 模糊查找。

### 单词抽查

- **随机抽查**：根据中文释义输入英文，可提交答案或显示答案。
- **随机选取**：直接显示单词完整信息，点击“下一个单词”继续。

### 设置

- 修改主题、字体大小、网络超时等。
- 保存后部分设置需要重启程序生效，可选择立即重启。

### 数据操作

- 数据库操作：备份、删除、从收藏重建、导入数据库。
- 收藏操作：备份、删除、从文件导入、从数据库重建。
- 页面会实时显示数据库和收藏的状态。

### 关于与帮助

- “关于”页面展示版本、作者、版权和 GPL 协议摘要。
- “帮助”页面显示软件自带的帮助文档。

## 数据与备份

程序数据默认保存在程序目录下的 `data` 文件夹中：

```
data/
├── backup/          # 备份文件
├── logs/            # 运行日志
├── user/            # 用户设置与收藏
│   ├── settings.ini
│   └── love.txt
└── wordbook.db      # 单词数据库
```

- **备份数据库**：将 `wordbook.db` 复制到 `backup` 目录。
- **备份收藏**：将收藏文件复制到 `backup` 目录。
- **迁移数据**：在新电脑上安装后，使用“导入数据库”和“从文件导入”恢复。

> 卸载程序时默认保留 `data` 目录中的用户数据，避免误删。

## 开发与构建

### 环境准备

- Python 3.8+
- PySide6 6.5+
- 依赖见 `requirements.txt`

### 运行

```bash
python main.py
```

或使用入口脚本：

```bash
python WordBook.py
```

### 打包

项目使用 PyInstaller 打包为独立可执行文件：

```powershell
# 在项目根目录执行
pyinstaller --clean --noconfirm WordBook.spec
# 或参考 build.ps1
```

打包完成后，可执行文件位于 `dist/` 目录。

### 制作安装包

使用 Inno Setup 6 编译 `setup.iss`：

1. 确保 `dist/` 目录已生成。
2. 准备 `LICENSE.txt`，内容为 GPL-3.0 全文（UTF-8 编码）。
3. 用 Inno Setup 打开 `setup.iss` 并编译，生成的安装包位于 `installer/` 目录。

## 许可证

本项目采用 **GNU General Public License v3.0 or later**（GPL-3.0-or-later）授权。

```
Copyright (C) 2025-2026 喵布

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

完整协议文本见项目根目录下的 `LICENSE` 文件，或访问 <https://www.gnu.org/licenses/gpl-3.0.txt>。

## 第三方依赖

- [PySide6](https://doc.qt.io/qtforpython/)：LGPL-3.0 / GPL-3.0
- [loguru](https://github.com/Delgan/loguru)：MIT
- [requests](https://requests.readthedocs.io/)：Apache-2.0
- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)：MIT
- [lxml](https://lxml.de/)：BSD-3-Clause

## 致谢

感谢所有开源项目的贡献者。
图标素材来自 [Pixiv](https://www.pixiv.net/artworks/112934352)，仅用于非商用，版权归原作者所有。

---

如有问题或建议，欢迎提交 [Issue](https://github.com/yourname/WordBook/issues)。
