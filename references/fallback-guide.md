# 无OpenCode环境下的Hexo文章恢复指南

如果你的AI不支持Skill功能，可以通过以下方式让任意AI（如ChatGPT、Claude网页版、Midorigin等）帮助恢复Hexo文章。

---

## 方法一：直接发送提示词给AI

复制以下提示词，发送给AI：

---

### 提示词模板

```
我需要将Hexo博客的HTML文件转换为Markdown格式。

## 任务说明

我有一个Hexo静态博客，目录结构如下：
- 博客根目录/
  - 2019/10/18/hexo/index.html  (文章1)
  - 2023/12/31/年终总结/index.html  (文章2)
  - ...其他年份的文章

每篇文章都是index.html，需要转换为.md文件。

## HTML结构特征

我使用的主题是 **Redefine**，具有以下HTML结构：

### 文章容器
```html
<div class="article-content markdown-body">
  <h1 class="article-title-regular">文章标题</h1>
  <div class="article-header">...作者信息，会被移除...</div>
  <p>正文内容...</p>
  <div class="code-container" data-rel="语言">
    <figure class="iseeu highlight 语言">
      <table><tr>
        <td class="gutter"><pre><span class="line">行号</span>...</pre></td>
        <td class="code"><pre><span class="line">代码内容</span>...</pre></td>
      </tr></table>
    </figure>
  </div>
</div>
```

### 元数据位置
- 标题：`<h1 class="article-title-regular">` 或 `<meta property="og:title">`
- 日期：`<meta property="article:published_time">` (格式: YYYY-MM-DDTHH:MM:SS.sssZ)
- 标签：所有包含 `/blog/tags/` 路径的 `<a>` 标签文本

### 需要移除的元素
- `<div class="post-copyright-info">` - 版权信息
- `<div class="article-nav">` - 导航
- `<div class="comment-container">` - 评论
- `<div class="article-header">` - 作者头像信息
- `<div class="post-tags-box">` - 底部标签

## 输出要求

对每一篇文章，输出标准Hexo Markdown格式：

```markdown
---
title: 文章标题
date: YYYY-MM-DD HH:MM:SS
tags: [标签1, 标签2]
---

# 文章标题

正文内容...

```语言
代码内容
```
```

## 代码块正确格式

代码块必须每行独立一行，不能有行号！

正确：
```yaml
deploy:
type: git
repo: https://example.com/repo.git
```

错误（有行号）：
```yaml
1 deploy:
2 type: git
3 repo: https://example.com/repo.git
```

---

请帮我分析并转换我上传的HTML文件。
```

---

## 方法二：提供完整提取代码

如果AI能生成代码，可以让AI生成以下Python脚本：

```python
from bs4 import BeautifulSoup
import markdownify
import re
import os

def convert_html_to_markdown(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 提取标题
    title_elem = soup.find('h1', class_='article-title-regular')
    if not title_elem:
        title_elem = soup.find('h1', class_='posttitle')
    title = title_elem.get_text(strip=True) if title_elem else 'Untitled'
    
    # 提取日期
    date = ''
    date_elem = soup.find('meta', property='article:published_time')
    if date_elem:
        date = date_elem.get('content', '')[:19].replace('T', ' ')
    
    # 提取标签
    tags = []
    for a in soup.find_all('a', href=lambda h: h and '/blog/tags/' in h):
        tag = a.get_text(strip=True).lstrip('#')
        if tag and tag not in tags:
            tags.append(tag)
    
    # 构建Front Matter
    front_matter = f"---\ntitle: {title}\ndate: {date}\n"
    if tags:
        front_matter += f"tags: [{', '.join(tags)}]\n"
    front_matter += "---\n\n"
    
    # 提取文章主体
    article = soup.find('div', class_='article-content')
    if not article:
        article = soup.find('div', class_='markdown-body')
    if not article:
        return None
    
    # 移除无关元素
    for cls in ['post-copyright-info', 'article-nav', 'comment-container', 
                'article-header', 'post-tags-box', 'article-content-container']:
        for elem in article.find_all(class_=re.compile(cls)):
            elem.decompose()
    
    # 移除第一个h1（已在标题中）
    first_h1 = article.find('h1')
    if first_h1:
        first_h1.decompose()
    
    # 处理代码块
    for code_container in article.find_all('div', class_='code-container'):
        lang = code_container.get('data-rel', '')
        figure = code_container.find('figure', class_=re.compile(r'highlight'))
        if figure:
            code_elem = figure.find('td', class_='code')
            if code_elem:
                lines = [span.get_text() for span in code_elem.find_all('span', class_=re.compile(r'^line')) if span.get_text()]
                code_block = f"\n```{lang}\n{chr(10).join(lines)}\n```\n"
                code_container.replace_with(code_block)
    
    # 转换为Markdown
    markdown_body = markdownify.markdownify(str(article), heading_style="ATX")
    return front_matter + re.sub(r'\n{3,}', '\n\n', markdown_body.strip())

# 使用示例
# html = open('index.html', 'r', encoding='utf-8').read()
# md = convert_html_to_markdown(html)
# open('output.md', 'w', encoding='utf-8').write(md)
```

---

## 方法三：批量处理脚本

如果需要批量转换整个博客，可以生成以下脚本：

```python
import os
from pathlib import Path

def convert_blog(source_dir, output_dir):
    """批量转换博客"""
    
    ignore_folders = {"about", "archives", "css", "friends", "images", 
                      "jpg", "js", "lib", "page", "png", "tags"}
    
    converted = []
    failed = []
    
    for root, dirs, files in os.walk(source_dir):
        # 跳过不需要的目录
        dirs[:] = [d for d in dirs if d not in ignore_folders]
        
        if 'index.html' in files:
            html_path = os.path.join(root, 'index.html')
            folder_name = os.path.basename(root)
            
            try:
                html = open(html_path, 'r', encoding='utf-8').read()
                md = convert_html_to_markdown(html)
                
                if md:
                    output_path = os.path.join(output_dir, f"{folder_name}.md")
                    open(output_path, 'w', encoding='utf-8').write(md)
                    converted.append(folder_name)
                else:
                    failed.append((folder_name, '未找到文章主体'))
            except Exception as e:
                failed.append((folder_name, str(e)))
    
    return converted, failed

# 使用
# converted, failed = convert_blog('D:/path/to/blog', 'D:/path/to/output')
# print(f"成功: {len(converted)}, 失败: {len(failed)}")
```

---

## 方法四：AI对话示例

如果AI不支持代码执行，可以按照以下对话流程获取转换后的内容：

### 对话示例

**用户**：
```
请帮我转换以下HTML内容为Markdown格式。文件位于博客的 2023/12/31/年终总结/index.html

[粘贴HTML内容的前500行]
```

**AI响应**：
```
我将帮您提取并转换这段内容...
[提取出Front Matter和正文]
```

**用户**：
```
很好，请继续提取代码块部分
```

**AI响应**：
```
[继续提取并转换代码块]
```

---

## 注意事项

1. **代码块必须每行独立** - 不能有行号前缀
2. **标签去重** - 移除重复的标签和`#`前缀
3. **保留图片路径** - 使用原始相对路径如 `/blog/images/xxx.png`
4. **中文编码** - 确保使用UTF-8编码保存文件
5. **Front Matter格式** - 必须是标准YAML格式

---

## 常见问题

Q: 转换后代码块显示错误怎么办？
A: 确保从 `td.code` 的 `span.line` 提取内容，而不是从 `td.gutter`

Q: 文章标题重复出现怎么办？
A: 在转换前移除文章主体内的第一个 `<h1>` 元素

Q: 标签出现 `[Pasted N lines]` 提示怎么办？
A: 删除所有包含 `[Pasted` 的文本元素

Q: 主题不兼容怎么办？
A: 使用html-analyzer skill分析具体结构，或发送HTML样本给AI进行诊断

---

## 联系支持

如果上述方法都无法解决您的问题，请：
1. 打包一份HTML样本（包含文章、代码块、标签等）
2. 描述具体的错误现象
3. 发送到 GitHub Issues: https://github.com/NANAFREE/Hexo-Phantom-Res/issues