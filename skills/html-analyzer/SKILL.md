---
name: html-analyzer
description: |
  Hexo博客HTML结构分析器。当用户提到以下情况时触发：
  - "分析我的主题"、"识别HTML结构"
  - "为什么转换失败"、"文章主体在哪"
  - "主题不兼容"、"选择器不对"
  - "帮我看看这个HTML"、"检测博客结构"
  - 用户上传了HTML文件并询问如何提取内容
  此技能用于诊断问题并提供针对性的转换方案。
---

# Hexo HTML 结构分析器

## 用途

当标准转换失败时，本技能用于深度分析任意Hexo主题生成的HTML结构，识别文章容器、元数据位置、代码块结构，并输出定制化的提取方案。

## 分析流程

### 1. 读取HTML样本

读取目标目录中至少3个不同的index.html文件（跨不同年份/主题），全面了解结构。

### 2. 识别关键元素

#### 文章容器分析
```python
# 尝试找到文章主体
selectors_to_try = [
    'article.post', 'div.post', 'article.article',
    'div.article-content', 'div.markdown-body',
    'div.post-content', 'section.post-content',
    'div.entry-content', 'div.post-body',
    '[class*="article"]', '[class*="post"]', '[class*="content"]'
]

for selector in selectors:
    elem = soup.select_one(selector)
    if elem and len(elem.get_text()) > 500:  # 文章通常超过500字符
        print(f"Found article container: {selector}")
        print(f"Class: {elem.get('class')}")
        print(f"ID: {elem.get('id')}")
        break
```

#### 元数据位置检测
- 搜索`<time>`标签（通常在article内或header内）
- 搜索`<meta property="article:">`标签（head区域）
- 搜索包含`/tags/`的链接（通常在文章底部或侧边栏）
- 搜索`data-published`或`datetime`属性

#### 代码块结构分析
```python
# 分析代码块的三层结构
code_structures = {
    'highlight_figure': soup.find_all('figure', class_=re.compile(r'highlight')),
    'code_container': soup.find_all('div', class_='code-container'),
    'pre_code': soup.find_all('pre'),
    'table_highlight': soup.find_all('table', class_=re.compile(r'highlight'))
}

for name, blocks in code_structures.items():
    if blocks:
        sample = blocks[0]
        print(f"{name}: found {len(blocks)} blocks")
        # 检查行号结构
        lines = sample.find_all('span', class_='line')
        print(f"  Line spans: {len(lines)}")
        # 检查语言标识
        lang_classes = [c for c in sample.get('class', []) if c not in ('highlight', 'iseeu')]
        print(f"  Language classes: {lang_classes}")
```

### 3. 输出诊断报告

```markdown
## HTML结构诊断报告

### 文章容器
- 标签: {tag}
- Class: {class}
- 位置: {path}
- 内容长度: {length}字符

### 元数据
- 标题元素: {selector}
- 日期元素: {selector}  
- 标签元素: {selector}

### 代码块
- 类型: {type}
- 语言标识位置: {location}
- 行号结构: {structure}

### 转换建议
针对此主题，推荐使用以下选择器和处理逻辑：
1. 文章容器: `{selector}`
2. 代码块提取: `{method}`
3. 需要额外清理的元素: {elements}
```

## 主题自动识别

内置常见主题识别：

| 主题名 | 特征class | 检测关键词 |
|-------|-----------|-----------|
| Redefine | `article-content`, `markdown-body` | `data-rel=` |
| Next | `post-content` | `highlight Sh` |
| Icarus | `article`, `post-content` | `language-` |
| Fluid | `article-content` | `hljs` |
| Matery | `post-detail` | `v的数字` |
| Astra | `entry-content` | `wp-block-code` |

## 输出定制提取方案

基于分析结果，输出可以直接使用的Python提取代码：

```python
def extract_for_theme_name(soup):
    """针对特定主题的提取函数"""
    
    # 文章容器
    article = soup.find('div', class_=re.compile(r'article-content'))
    
    # 清理
    for cls in ['post-copyright-info', 'article-nav', 'comment-container']:
        for elem in article.find_all(class_=re.compile(cls)):
            elem.decompose()
    
    # 代码块
    for code_container in article.find_all('div', class_='code-container'):
        # 提取逻辑
        ...
    
    return article
```

## 使用场景

1. **转换失败诊断**：用户说"转换失败了" → 分析HTML找问题
2. **新主题适配**：用户说"我的主题和你的不一样" → 识别并生成方案
3. **批量验证**：检查多个文件确认主题结构一致性
4. **选择器调试**：测试不同选择器哪个更有效