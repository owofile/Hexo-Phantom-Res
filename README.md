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

## Introduction

Hexo-Phantom-Res is an intelligent Hexo blog recovery toolkit with automatic theme detection and conversion support.

**Core Features:**
- Auto-identify 10+ popular Hexo themes
- Smart extraction of metadata (title, date, tags)
- Proper code block handling (preserve language hints, remove line numbers)
- Output standard Hexo Markdown format

## Quick Start

### Method 1: GUI Interface

```bash
pip install beautifulsoup4 markdownify
python "Hexo Phantom Res.py"
```

### Method 2: Command Line

```bash
pip install beautifulsoup4 markdownify
python scripts/converter.py
```

### Method 3: Multi-Agent Coordinator

```bash
python scripts/agent_coordinator.py <source_dir> <output_dir>
```

## Project Structure

```
Hexo-Phantom-Res/
├── Hexo Phantom Res.py      # GUI main program
├── scripts/
│   ├── converter.py         # CLI converter
│   └── agent_coordinator.py # Multi-agent coordinator
├── skills/
│   ├── hexo-converter/      # Core conversion skill
│   └── html-analyzer/       # HTML structure analyzer skill
├── references/
│   ├── theme-patterns.md    # Theme structure reference
│   └── fallback-guide.md    # Guide for non-AI environments
├── evals/                   # Test evaluation files
└── README.md
```

## Supported Themes

| Theme | Features | Status |
|-------|----------|--------|
| Redefine | `div.article-content`, `div.code-container` | ✅ Full |
| Next | `div.post-content`, `figure.highlight` | ✅ Full |
| Icarus | `article.post`, `pre.code` | ✅ Full |
| Fluid | `div.article-content`, `hljs` | ✅ Full |
| Matery | `div.post-detail` | ✅ Full |
| Landscape | `article.post`, `table.highlight` | ✅ Full |
| Others | Generic selector adaptation | ⚠️ Needs analysis |

## OpenCode Skills

Place `skills/` folder into OpenCode's skills directory to use:

**hexo-converter**: Hexo HTML to Markdown intelligent converter
- Auto-identify theme type
- Multi-selector adaptation
- Smart code block processing

**html-analyzer**: HTML structure analyzer
- Diagnose conversion issues
- Generate custom extraction solutions
- Analyze theme characteristics

## Non-OpenCode Usage

If you don't have OpenCode or other AI with Skill support, refer to:
- `references/fallback-guide.md` - Complete prompt templates
- Any AI (ChatGPT, Claude, etc.) can help convert following the guide

## Output Format

Input: Hexo-generated `index.html`
Output: Standard Hexo Markdown

```markdown
---
title: Article Title
date: 2023-12-31 13:34:14
tags: [tag1, tag2]
---

# Article Title

Content...

```yaml
deploy:
type: git
repo: https://example.com/repo.git
```
```

## License

MIT License

## Contact

- **GitHub Issues**: [Submit an Issue](https://github.com/NANAFREE/Hexo-Phantom-Res/issues)