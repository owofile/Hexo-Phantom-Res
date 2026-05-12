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

## はじめに

Hexo-Phantom-Res は、Hexo テーマの HTML 構造を自動識別し、変換をサポートする智能的な Hexo ブログ恢复ツールキットです。

**主な機能：**
- 10+ の主流 Hexo テーマを自動識別
- メタデータ（タイトル、日付、タグ）の智能抽出
- コードブロックの適切な処理（言語标识を保持、行番号を削除）
- 標準 Hexo Markdown 形式を出力

## クイックスタート

### 方法1：GUI インターフェース

```bash
pip install beautifulsoup4 markdownify
python "Hexo Phantom Res.py"
```

### 方法2：コマンドライン

```bash
pip install beautifulsoup4 markdownify
python scripts/converter.py
```

### 方法3：マルチ Agent コーディネーター

```bash
python scripts/agent_coordinator.py <ソースディレクトリ> <出力ディレクトリ>
```

## プロジェクト構造

```
Hexo-Phantom-Res/
├── Hexo Phantom Res.py      # GUI メprograms
├── scripts/
│   ├── converter.py         # CLI 変換器
│   └── agent_coordinator.py # マルチ Agent コーディネーター
├── skills/
│   ├── hexo-converter/      # コア変換スキル
│   └── html-analyzer/       # HTML 構造分析スキル
├── references/
│   ├── theme-patterns.md    # テーマ構造リファレンス
│   └── fallback-guide.md    # 非 AI 環境ガイド
├── evals/                   # テスト評価ファイル
└── README.md
```

## 対応テーマ

| テーマ | 特徴 | 状態 |
|-------|------|------|
| Redefine | `div.article-content`, `div.code-container` | ✅ 完全対応 |
| Next | `div.post-content`, `figure.highlight` | ✅ 完全対応 |
| Icarus | `article.post`, `pre.code` | ✅ 完全対応 |
| Fluid | `div.article-content`, `hljs` | ✅ 完全対応 |
| Matery | `div.post-detail` | ✅ 完全対応 |
| Landscape | `article.post`, `table.highlight` | ✅ 完全対応 |
| その他 | 汎用セレクター適応 | ⚠️ 分析が必要 |

## OpenCode スキル

`skills/` フォルダを OpenCode の skills ディレクトリに配置することで使用できます：

**hexo-converter**: Hexo HTML から Markdown への智能変換器
- テーマ类型を自動識別
- 複数のセレクターに適応
- コードブロックの智能処理

**html-analyzer**: HTML 構造分析器
- 変換の問題を診断
- カスタム抽出ソリューションを生成
- テーマの特性を分析

## 非 OpenCode 環境での使用

OpenCode またはその他のスキル支持的 AI をお持ちでない場合は、以下を参照してください：
- `references/fallback-guide.md` - 完全なプロンプトテンプレート
- 任意の AI（ChatGPT、Claude など）がガイドに従って変換を手伝うことができます

## 出力形式

入力：Hexo 生成の `index.html`
出力：標準 Hexo Markdown

```markdown
---
title: 記事タイトル
date: 2023-12-31 13:34:14
tags: [タグ1, タグ2]
---

# 記事タイトル

コンテンツ...

```yaml
deploy:
type: git
repo: https://example.com/repo.git
```
```

## ライセンス

MIT License

## お問い合わせ

- **GitHub Issues**: [問題を提交](https://github.com/NANAFREE/Hexo-Phantom-Res/issues)