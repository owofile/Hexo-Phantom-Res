# Hexo HTML 转 Markdown 转换器

[English](./README.md) | [中文](./README.zh.md) | [日本語](./README.ja.md)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/) [![Beautiful Soup](https://img.shields.io/badge/Beautiful_Soup-4.0+-green)](https://www.crummy.com/software/BeautifulSoup/) [![Markdownify](https://img.shields.io/badge/Markdownify-0.11.6-orange)](https://github.com/matthewwithanm/python-markdownify) [![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 简介

Hexo HTML 转 Markdown 转换器是一个 Python 脚本，用于将 Hexo 生成的 HTML 文件转换为 Markdown 文件。该工具提供了一个简单的 GUI 界面，用户可以选择源目录和输出目录，并通过单击按钮完成文件转换。转换过程中会保留文章元数据（如标题、日期和标签），并正确处理代码块。

## 使用指南

### 1. 安装依赖项

在运行工具之前，请确保已安装所需的 Python 库：

```bash
pip install beautifulsoup4 markdownify

```
2. 下载脚本
可以从 GitHub 或其他代码托管平台下载 Hexo Phantom Res.py 脚本。

3. 运行脚本
确保已安装所需依赖项，然后运行脚本：

```bash
bash
python Hexo Phantom Res.py
```

4. 使用 GUI 界面
选择源目录：
点击“选择源文件夹”按钮，选择包含 Hexo 生成的 HTML 文件的目录。
脚本将自动查找目录及其子目录中的所有 index.html 文件。
选择输出目录：
点击“选择输出位置”按钮，选择转换后的 Markdown 文件将保存的目录。
开始转换：
点击“开始转换”按钮，开始将 HTML 文件转换为 Markdown 文件。
进度条将显示转换进度，日志区域将记录每一步的状态。
5. 查看结果
转换完成后，可以在指定的输出目录中找到生成的 Markdown 文件。

示例
假设你的源目录结构如下：
```

source_dir/
├── 2019/
│   └── 10/
│       └── 18/
│           └── hexo/
│               └── index.html
└── 2020/
    └── 01/
        └── 01/
            └── newblog/
                └── index.html

```

运行脚本并选择上述源目录和输出目录后，生成的 Markdown 文件将保存在输出目录中，文件名为 hexo.md 和 newblog.md。

源目录：确保源目录包含 Hexo 生成的 HTML 文件，且文件名为 index.html。
输出目录：确保输出目录存在，或者脚本有权限创建新目录。
代码块处理：工具会自动处理 Hexo 的高亮代码块和其他常规代码块，确保代码在输出中正确显示。

我们希望这个工具能帮助你顺利地将 Hexo 生成的 HTML 文件转换为 Markdown 文件！如果你有任何建议或改进建议，请随时告知我们。