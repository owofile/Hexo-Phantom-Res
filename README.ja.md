# Hexo HTML to Markdown コンバーター

<p align="center">
   <img src="./logo.png" alt="ロゴ" width="200">
</p>

<p align="center">
   <a href="./README.md">English</a> | <a href="./README.zh.md">中文</a> | <a href="./README.ja.md">日本語</a>
</p>

<p align="center">
   <img src="https://img.shields.io/badge/Python-3.8%2B-blue?logo=python" alt="Python">
   <img src="https://img.shields.io/badge/Beautiful_Soup-4.0+-green" alt="Beautiful Soup">
   <img src="https://img.shields.io/badge/Markdownify-0.11.6-orange" alt="Markdownify">
   <img src="https://img.shields.io/badge/License-MIT-yellow" alt="ライセンス">
</p>

## はじめに

Hexo HTML to Markdown コンバーターは、Python スクリプトを使用して Hexo によって生成された HTML ファイルを Markdown ファイルに変換します。このツールは、ユーザーがソースディレクトリと出力ディレクトリを選択し、単一のクリックでファイルを変換できる簡単な GUI インターフェースを提供します。変換プロセスでは、タイトル、日付、タグなどの記事のメタデータが保持され、コードブロックも正しく処理されます。

## 使用ガイド

### 1. 依存関係のインストール

ツールを実行する前に、必要な Python ライブラリがインストールされていることを確認してください：


```bash
pip install beautifulsoup4 markdownify
```
2. スクリプトのダウンロード
Hexo Phantom Res.py スクリプトを GitHub または他のコードホスティングプラットフォームからダウンロードできます。

3. スクリプトの実行
必要な依存関係がインストールされていることを確認したら、スクリプトを実行します：

```bash
bash
python Hexo Phantom Res.py
```

4. GUI インターフェースの使用
ソースディレクトリの選択:
「ソースフォルダを選択」ボタンをクリックし、Hexo によって生成された HTML ファイルを含むディレクトリを選択します。
スクリプトは自動的にディレクトリおよびサブディレクトリ内のすべての index.html ファイルを検索します。
出力ディレクトリの選択:
「出力位置を選択」ボタンをクリックし、変換後の Markdown ファイルが保存されるディレクトリを選択します。
変換の開始:
「変換を開始」ボタンをクリックして、HTML ファイルから Markdown ファイルへの変換を開始します。
進行状況バーは変換の進行状況を表示し、ログ領域は各ステップの状態を記録します。
5. 結果の確認
変換が完了したら、指定した出力ディレクトリに生成された Markdown ファイルを見つけることができます。

例
ソースディレクトリの構造が次のようになっているとします：

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

上記のソースディレクトリと出力ディレクトリを選択してスクリプトを実行すると、生成された Markdown ファイルは出力ディレクトリに保存され、ファイル名は hexo.md および newblog.md になります。

ソースディレクトリ: ソースディレクトリには Hexo によって生成された HTML ファイルが含まれており、ファイル名は index.html である必要があります。
出力ディレクトリ: 出力ディレクトリが存在するか、またはスクリプトが新しいディレクトリを作成する権限があることを確認してください。
コードブロックの処理: このツールは Hexo のハイライトコードブロックおよびその他の一般的なコードブロックを自動的に処理し、出力でコードが正しく表示されるようにします。
このツールが Hexo によって生成された HTML ファイルを Markdown ファイルにスムーズに変換できるようにお手伝いします。何か提案や改善点があれば、いつでもお知らせください。