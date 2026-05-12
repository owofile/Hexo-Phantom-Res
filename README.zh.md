# Hexo-Phantom-Res

<p align="center">
   <img src="./logo.png" alt="Logo" width="200">
</p>

<p align="center">
   <a href="./README.md">English</a> | <a href="./README.zh.md">中文</a> | <a href="./README.ja.md">日本語</a>
</p>

<p align="center">
   <img src="https://img.shields.io/badge/Python-3.8%2B-blue?logo=python" alt="Python">
   <img src="https://img.shields.io/badge/Beautiful_Soup-4.0+-green" alt="Beautiful Soup">
   <img src="https://img.shields.io/badge/Markdownify-0.11.6-orange" alt="Markdownify">
   <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

## 简介

Hexo-Phantom-Res 是一个智能 Hexo 文章恢复工具包，支持多种 Hexo 主题的 HTML 结构自动识别与转换。

**核心功能：**
- 自动识别 10+ 种主流 Hexo 主题
- 智能提取文章元数据（标题、日期、标签）
- 正确处理代码块（保留语言标识、清除行号）
- 输出标准 Hexo Markdown 格式

## 快速开始

### 方式一：GUI 图形界面

```bash
pip install beautifulsoup4 markdownify
python "Hexo Phantom Res.py"
```

### 方式二：命令行脚本

```bash
pip install beautifulsoup4 markdownify
python scripts/converter.py
```

### 方式三：多 Agent 协调器

```bash
python scripts/agent_coordinator.py <源目录> <输出目录>
```

## 项目结构

```
Hexo-Phantom-Res/
├── Hexo Phantom Res.py      # GUI 主程序
├── scripts/
│   ├── converter.py         # 命令行转换器
│   └── agent_coordinator.py # 多 Agent 协调器
├── skills/
│   ├── hexo-converter/      # 核心转换 Skill
│   └── html-analyzer/       # HTML 结构分析 Skill
├── references/
│   ├── theme-patterns.md    # 主题结构参考
│   └── fallback-guide.md    # 非 AI 环境使用指南
├── evals/                   # 测试评估文件
└── README.md
```

## 支持的主题

| 主题 | 特征 | 支持状态 |
|------|------|---------|
| Redefine | `div.article-content`, `div.code-container` | ✅ 完全支持 |
| Next | `div.post-content`, `figure.highlight` | ✅ 完全支持 |
| Icarus | `article.post`, `pre.code` | ✅ 完全支持 |
| Fluid | `div.article-content`, `hljs` | ✅ 完全支持 |
| Matery | `div.post-detail` | ✅ 完全支持 |
| Landscape | `article.post`, `table.highlight` | ✅ 完全支持 |
| 其他主题 | 通用选择器适配 | ⚠️ 需要分析 |

## OpenCode Skills

将 `skills/` 目录放入 OpenCode 的 skills 目录即可使用：

**hexo-converter**: Hexo HTML 转 Markdown 智能转换器
- 自动识别主题类型
- 适配多种选择器
- 智能代码块处理

**html-analyzer**: HTML 结构分析器
- 诊断转换问题
- 生成定制提取方案
- 分析主题特征

## 非 OpenCode 环境使用

如果没有 OpenCode 或其他支持 Skill 的 AI，请参考：
- `references/fallback-guide.md` - 完整的提示词模板
- 任意 AI（ChatGPT、Claude 等）都能按照指南帮助转换

## 输出格式

输入：Hexo 生成的 `index.html`
输出：标准 Hexo Markdown

```markdown
---
title: 文章标题
date: 2023-12-31 13:34:14
tags: [标签1, 标签2]
---

# 文章标题

正文内容...

```yaml
deploy:
type: git
repo: https://example.com/repo.git
```
```

## 许可证

MIT License

## 联系方式

- **GitHub Issues**: [提交问题](https://github.com/NANAFREE/Hexo-Phantom-Res/issues)