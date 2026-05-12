# Hexo主题HTML结构参考

本文档记录主流Hexo主题的HTML结构特征，帮助快速适配转换器。

---

## Redefine 主题

**特征**：
- 文章容器：`div.article-content` + `div.markdown-body`
- 代码块：`div.code-container data-rel="语言"` + `figure.iseeu.highlight.*`
- 行号：在`td.gutter`中，与`td.code`并列

**示例HTML**：
```html
<div class="article-content markdown-body px-2 sm:px-6 md:px-8 pb-8">
  <h1 id="标题">标题</h1>
  <p>正文内容...</p>
  
  <div class="code-container" data-rel="Sh">
    <figure class="iseeu highlight sh">
      <table><tr>
        <td class="gutter">
          <pre><span class="line">1</span><br><span class="line">2</span><br></pre>
        </td>
        <td class="code">
          <pre><span class="line">console.log('hello')</span><br></pre>
        </td>
      </tr></table>
    </figure>
  </div>
</div>
```

**提取方案**：
```python
article = soup.find('div', class_=re.compile(r'article-content|markdown-body'))
code_container = article.find('div', class_='code-container')
lang = code_container.get('data-rel', '')
code_elem = code_container.find('td', class_='code')
lines = [span.get_text() for span in code_elem.find_all('span', class_='line') if span.get_text()]
```

---

## Next 主题

**特征**：
- 文章容器：`div.post-content` 或 `div.article-content`
- 代码块：`figure.highlight` + `table` 结构
- 语言标识在figure的class中（如`highlight Sh`）

**示例HTML**：
```html
<article class="post">
  <div class="post-content">
    <h1>标题</h1>
    <figure class="highlight Sh">
      <table><tr>
        <td class="gutter"><pre>...</pre></td>
        <td class="code"><pre><span class="line">代码</span></pre></td>
      </tr></table>
    </figure>
  </div>
</article>
```

**提取方案**：
```python
article = soup.find('div', class_='post-content')
for figure in article.find_all('figure', class_=re.compile(r'highlight')):
    code_elem = figure.find('td', class_='code')
    lang = [c for c in figure.get('class', []) if c not in ('highlight', 'iseeu')][0]
```

---

## Icarus 主题

**特征**：
- 文章容器：`article.post` 或 `div.article`
- 代码块：`div.highlight` > `pre` > `code`
- 语言标识在code的class中（如`language-javascript`）

**示例HTML**：
```html
<article class="post">
  <header>...</header>
  <div class="article-content">
    <h1>标题</h1>
    <div class="highlight javascript">
      <pre><code class="language-javascript">代码</code></pre>
    </div>
  </div>
</article>
```

**提取方案**：
```python
article = soup.find('article', class_='post')
for pre in article.find_all('pre'):
    code = pre.find('code')
    lang = ''
    for cls in code.get('class', []):
        if cls.startswith('language-'):
            lang = cls.split('-')[1]
            break
```

---

## Fluid 主题

**特征**：
- 文章容器：`div.article-content`
- 代码块：`div.highlight` + `pre`
- 带`hljs`类名

**示例HTML**：
```html
<div class="article-content">
  <h1>标题</h1>
  <div class="highlight hljs-center">
    <pre><code class="language-python">代码</code></pre>
  </div>
</div>
```

---

## Landscape 主题

**特征**：
- 文章容器：`article.post`
- 代码块：`table.highlight`
- 较老的默认主题

**示例HTML**：
```html
<article class="post">
  <header class="article-header">...</header>
  <div class="article-body">
    <h1>标题</h1>
    <table class="highlight">
      <tbody>
        <tr><td class="code"><pre><span class="line">代码</span></pre></td></tr>
      </tbody>
    </table>
  </div>
</article>
```

---

## 通用提取模板

当主题未知时，按优先级尝试：

```python
def find_article_container(soup):
    """通用文章容器查找"""
    # 优先级列表
    candidates = [
        {'tag': 'div', 'class': 'article-content'},
        {'tag': 'div', 'class': 'markdown-body'},
        {'tag': 'div', 'class': 'post-content'},
        {'tag': 'article', 'class': 'post'},
        {'tag': 'div', 'class': 'post'},
        {'tag': 'article', 'class': 'article'},
        {'tag': 'div', 'class': 'entry-content'},
        {'tag': 'div', 'class': 'post-body'},
        {'tag': 'div', 'attrs': {'id': 'content'}},
        {'tag': 'div', 'attrs': {'id': 'article-content'}},
    ]
    
    for c in candidates:
        if c.get('class'):
            elem = soup.find(c['tag'], class_=c['class'])
        elif c.get('attrs'):
            elem = soup.find(c['tag'], attrs=c['attrs'])
        else:
            elem = soup.find(c['tag'])
        
        if elem and len(elem.get_text(strip=True)) > 500:
            return elem
    
    return None

def extract_code_blocks(article):
    """通用代码块提取"""
    results = []
    
    # 尝试 div.code-container 格式
    for cc in article.find_all('div', class_='code-container'):
        lang = cc.get('data-rel', '')
        code_elem = cc.find('td', class_='code')
        if code_elem:
            lines = [s.get_text() for s in code_elem.find_all('span', class_='line') if s.get_text()]
            results.append({'lang': lang, 'lines': lines, 'format': 'code-container'})
            continue
        
        code = cc.find('code')
        if code:
            results.append({'lang': lang, 'lines': code.get_text().split('\n'), 'format': 'code-container'})
    
    # 尝试 figure.highlight 格式
    for fig in article.find_all('figure', class_=re.compile(r'highlight')):
        if fig.find_parent('div', class_='code-container'):
            continue
        code_elem = fig.find('td', class_='code')
        if code_elem:
            lang = [c for c in fig.get('class', []) if c not in ('highlight', 'iseeu') and not c.startswith('highlight')]
            lines = [s.get_text() for s in code_elem.find_all('span', class_='line') if s.get_text()]
            results.append({'lang': lang[0] if lang else '', 'lines': lines, 'format': 'figure'})
    
    # 尝试 pre/code 格式
    for pre in article.find_all('pre'):
        if pre.find_parent('figure') or pre.find_parent('div', class_='code-container'):
            continue
        code = pre.find('code')
        if code:
            lang = ''
            for cls in code.get('class', []):
                if cls.startswith('language-'):
                    lang = cls.split('-')[1]
                    break
            results.append({'lang': lang, 'lines': code.get_text().split('\n'), 'format': 'pre-code'})
    
    return results
```

---

## 元数据提取对照表

| 信息 | Redefine | Next | Icarus | 通用 |
|-----|---------|------|--------|-----|
| 标题 | `h1.article-title-regular` | `h1.post-title` | `h1` in `article` | `meta[property="og:title"]` |
| 日期 | `time.dt-published` | `time.post-time` | `time` | `meta[property="article:published_time"]` |
| 标签 | `a[href*="/tags/"]` | `a[href*="/tags/"]` | `a.tag` | 所有包含`/tags/`的链接 |

---

## 清理元素对照表

| 元素class/id | 含义 | 是否需要移除 |
|-------------|------|------------|
| `post-copyright-info` | 版权声明 | ✅ |
| `article-nav` | 上一篇/下一篇 | ✅ |
| `article-prev` | 上一页导航 | ✅ |
| `article-next` | 下一页导航 | ✅ |
| `comment-container` | 评论区域 | ✅ |
| `article-header` | 作者信息+头像 | ✅ |
| `post-tags-box` | 底部标签列表 | ✅ |
| `toc-content-container` | 目录 | ✅ |
| `article-content-container` | 包含整个内容的外层 | ⚠️小心 |
| `post-tools` | 工具栏 | ✅ |