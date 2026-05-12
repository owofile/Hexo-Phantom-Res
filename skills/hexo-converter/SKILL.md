---
name: hexo-converter
description: |
  Hexo HTML转Markdown智能转换器。当用户提到以下情况时触发：
  - "转换Hexo博客"、"恢复博客"、"HTML转Markdown"
  - "我的博客主题不兼容"、"转换失败"
  - "批量转换文章"、"提取博客内容"
  - 任何涉及从Hexo生成的静态HTML文件中恢复Markdown文章的任务
  - 用户上传了blog目录或index.html并要求提取文章
  - 用户询问"如何恢复Hexo文章"、"Hexo文章迁移"
  这是核心转换技能，支持多种Hexo主题的HTML结构自动识别。
---

# Hexo HTML 转 Markdown 智能转换器

## 核心能力

本技能能够智能分析任意Hexo主题生成的HTML文章，提取元数据（title、date、tags），解析文章主体内容，处理代码块，并输出标准Hexo Markdown格式。

## 工作流程

### 第一步：分析HTML结构

读取目标目录的index.html文件，分析以下关键要素：

1. **文章容器选择器** - 尝试识别文章主体所在容器：
   - `article.post`, `div.post`, `div.article-content`, `div.markdown-body`
   - `div.post-content`, `section.post-content`, `div.entry-content`
   - 带有id的容器：`id="content"`, `id="article-content"`, `id="post-content"`

2. **元数据提取**：
   - 标题：从`<h1 class="posttitle">`、`<h1 class="article-title-regular">`或`<meta property="og:title">`提取
   - 日期：从`<time class="dt-published">`或`<meta property="article:published_time">`提取
   - 标签：从`<a class="p-category" rel="tag">`或包含`/tags/`路径的链接提取

3. **代码块识别**：
   - `highlight`类代码块：`<figure class="highlight">`或`<div class="code-container">`
   - 提取语言标识符（class中的语言名如`Sh`, `Yaml`, `JavaScript`）
   - 代码行从`<span class="line">`或`<td class="code">`中的`<span>`提取

### 第二步：提取文章内容

使用BeautifulSoup解析HTML时：
1. 找到文章容器后，移除无关元素：
   - `post-copyright-info`（版权信息）
   - `article-nav`, `article-prev`, `article-next`（导航）
   - `comment-container`（评论区域）
   - `article-header`（作者信息、头像）
   - `post-tags-box`（底部标签）
   - `toc-content-container`（目录）
   - `post-tools`（工具栏）

2. 提取第一个`<h1>`作为标题（已单独处理）

3. 处理代码块替换：
   ```python
   # 伪代码示例
   for code_container in soup.find_all('div', class_='code-container'):
       lang = code_container.get('data-rel', '')
       code_elem = code_container.find('td', class_='code')
       lines = [span.get_text() for span in code_elem.find_all('span', class_='line') if span.get_text()]
       code_block = f"\n```{lang}\n{chr(10).join(lines)}\n```\n"
       code_container.replace_with(code_block)
   ```

### 第三步：生成Markdown

1. **Front Matter格式**：
   ```yaml
   ---
   title: {标题}
   date: {日期，格式YYYY-MM-DD HH:MM:SS}
   tags: [{标签1}, {标签2}, ...]
   ---
   ```

2. **正文转换**：
   - 使用markdownify将剩余HTML转为Markdown
   - 处理链接：保留外部链接，移除内部标签链接
   - 清理多余空行（超过2个连续空行合并为2个）

3. **输出文件命名**：
   - 使用所在文件夹名称作为文件名
   - 保存为`{文件夹名}.md`

## 主题适配指南

### 常见主题识别模式

| 主题 | 文章容器class | 代码块结构 |
|------|--------------|-----------|
| Redefine | `div.article-content` + `markdown-body` | `div.code-container` > `figure.highlight` |
| Next | `div.post-content` | `figure.highlight` > `td.code` > `span.line` |
| Icarus | `article.post` | `div.highlight` > `pre` > `code` |
| Landscape | `article.post` | `table.highlight` > `td.code` |

### 代码块修复模式

**Redefine主题代码块**（当前博客使用）:
```html
<div class="code-container" data-rel="Sh">
  <figure class="iseeu highlight sh">
    <table><tr>
      <td class="gutter"><pre><span class="line">1</span>...</pre></td>
      <td class="code"><pre><span class="line">code here</span>...</pre></td>
    </tr></table>
  </figure>
</div>
```
提取方式：找到`td.code`，遍历`span.line`

**常规highlight块**:
```html
<figure class="highlight Sh">
  <table><tr>
    <td class="gutter">...</td>
    <td class="code"><pre><span class="line">...</span></pre></td>
  </tr></table>
</figure>
```

## 常见问题处理

### 问题1：找不到文章主体
**原因**：主题使用了非标准class名
**解决**：尝试多种选择器组合，或使用正则匹配部分class名：
```python
article = soup.find('div', class_=re.compile(r'article|post|content', re.I))
```

### 问题2：代码块显示错误
**原因**：语言标识符不匹配或行号未清除
**解决**：确保从正确的td提取代码，清除行号span，只保留内容

### 问题3：多标签重复
**原因**：标签同时出现在正文和meta信息中
**解决**：对标签去重并移除`#`前缀

### 问题4：出现[Pasted N lines]提示
**原因**：Hexo渲染时保留了复制粘贴提示
**解决**：在转换前删除包含`[Pasted`的所有文本元素

## 验证输出

转换完成后检查输出文件：
1. Front Matter完整且格式正确
2. 代码块有正确的语言标识和内容
3. 无多余的作者信息、版权、导航元素
4. 中文编码正确显示
5. 图片路径保持原始相对路径

## 参考文件

- `references/theme-patterns.md` - 各主流Hexo主题的HTML结构模式
- `references/code-block-fixes.md` - 代码块修复详细教程