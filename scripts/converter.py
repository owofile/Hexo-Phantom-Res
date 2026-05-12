from bs4 import BeautifulSoup
import markdownify
import re
import os
import sys

def convert_html_to_markdown(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    title_elem = soup.find('h1', class_='article-title-regular')
    if not title_elem:
        title_elem = soup.find('h1', class_='posttitle')
    title = title_elem.get_text(strip=True) if title_elem else 'Untitled'
    
    date = ''
    date_elem = soup.find('time', {'class': 'dt-published'})
    if date_elem:
        date = date_elem['datetime']
    else:
        meta_dates = soup.find_all('span', class_='desktop')
        for m in meta_dates:
            txt = m.get_text(strip=True)
            if txt and re.match(r'\d{4}-\d{2}-\d{2}', txt):
                date = txt
                break
    
    tags = [tag.get_text(strip=True).lstrip('#') for tag in soup.find_all('a', href=lambda h: h and '/tags/' in h and '/blog/tags/' in h)]
    
    front_matter = "---\n"
    front_matter += f"title: {title}\n"
    front_matter += f"date: {date}\n"
    if tags:
        front_matter += f"tags: [{', '.join(tags)}]\n"
    front_matter += "---\n\n"
    
    article = None
    article_selectors = [
        {'tag': 'div', 'class': 'article-content'},
        {'tag': 'div', 'class': 'markdown-body'},
        {'tag': 'article', 'class': 'post'},
        {'tag': 'div', 'class': 'post'},
        {'tag': 'div', 'class': 'post-content'},
        {'tag': 'div', 'class': 'article-content'},
        {'tag': 'div', 'class': 'entry-content'},
        {'tag': 'div', 'class': 'post-body'},
        {'tag': 'section', 'class': 'post-content'},
        {'tag': 'div', 'attrs': {'id': 'post-content'}},
        {'tag': 'div', 'attrs': {'id': 'article-content'}},
        {'tag': 'div', 'attrs': {'id': 'content'}},
    ]
    
    for selector in article_selectors:
        if selector.get('class'):
            article = soup.find(selector['tag'], class_=re.compile(selector['class']))
        elif selector.get('attrs'):
            article = soup.find(selector['tag'], attrs=selector['attrs'])
        else:
            article = soup.find(selector['tag'])
        if article:
            break
    
    if not article:
        return None
    
    for cls in ['post-copyright-info', 'article-nav', 'comment-container', 'article-header',
                'post-tags-box', 'toc-content-container', 'article-content-container',
                'article-prev', 'article-next', 'post-tools']:
        for elem in article.find_all(class_=re.compile(cls)):
            elem.decompose()
    
    for elem in article.find_all(text=lambda t: t and '[Pasted' in t):
        parent = elem.parent
        if parent:
            parent.decompose()
    
    first_h1 = article.find('h1')
    if first_h1:
        first_h1.decompose()
    
    for code_container in article.find_all('div', class_='code-container'):
        lang = code_container.get('data-rel', '')
        figure = code_container.find('figure', class_=re.compile(r'highlight'))
        if figure:
            code_elem = figure.find('td', class_='code')
            if code_elem:
                lines = [span.get_text() for span in code_elem.find_all('span', class_=re.compile(r'^line')) if span.get_text()]
                code_block = f"\n```{lang}\n{chr(10).join(lines)}\n```\n"
                code_container.replace_with(code_block)
        else:
            code = code_container.find('code')
            if code:
                code_container.replace_with(f"\n```{lang}\n{code.get_text()}\n```\n")
    
    for figure in article.find_all('figure', class_=re.compile(r'highlight')):
        if figure.find_parent('div', class_='code-container'):
            continue
        code_elem = figure.find('td', class_='code')
        if code_elem:
            lang_classes = [cls for cls in figure.get('class', []) if cls not in ('highlight', 'iseeu') and not cls.startswith('highlight')]
            lang = lang_classes[0] if lang_classes else ''
            lines = [span.get_text() for span in code_elem.find_all('span', class_=re.compile(r'^line')) if span.get_text()]
            code_block = f"\n```{lang}\n{chr(10).join(lines)}\n```\n"
            figure.replace_with(code_block)
    
    for pre in article.find_all('pre'):
        if pre.find_parent('figure', class_=re.compile(r'highlight')) or pre.find_parent('div', class_='code-container'):
            continue
        code = pre.find('code')
        if code:
            lang = ''
            for cls in code.get('class', []):
                if cls.startswith('language-'):
                    lang = cls.split('-')[1]
                    break
            code_block = f"\n```{lang}\n{code.get_text()}\n```\n"
            pre.replace_with(code_block)
        else:
            pre.replace_with(f"\n```\n{pre.get_text()}\n```\n")
    
    markdown_body = markdownify.markdownify(str(article), heading_style="ATX", links_callback=lambda href, text: href if href and not href.startswith('/blog/tags') else None)
    full_markdown = front_matter + re.sub(r'\n{3,}', '\n\n', markdown_body.strip())
    return full_markdown

def convert_blog(source_dir, output_dir):
    """批量转换博客"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    ignore_folders = {"about", "archives", "css", "friends", "images", "jpg", "js", "lib", "page", "png", "tags"}
    
    converted = []
    failed = []
    total = 0
    
    for root_dir, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in ignore_folders]
        for file in files:
            if file == "index.html":
                total += 1
    
    if total == 0:
        print("未找到任何index.html文件")
        return [], []
    
    current = 0
    for root_dir, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in ignore_folders]
        for file in files:
            if file == "index.html":
                current += 1
                html_file = os.path.join(root_dir, file)
                folder_name = os.path.basename(root_dir)
                
                try:
                    with open(html_file, 'r', encoding='utf-8') as f:
                        html = f.read()
                    
                    md_content = convert_html_to_markdown(html)
                    if md_content:
                        md_file_path = os.path.join(output_dir, f"{folder_name}.md")
                        with open(md_file_path, 'w', encoding='utf-8') as f:
                            f.write(md_content)
                        converted.append(folder_name)
                        print(f"[{current}/{total}] 成功: {folder_name}.md")
                    else:
                        failed.append((folder_name, '未找到文章主体'))
                        print(f"[{current}/{total}] 失败: {folder_name} - 未找到文章主体")
                        
                except Exception as e:
                    failed.append((folder_name, str(e)))
                    print(f"[{current}/{total}] 失败: {folder_name} - {str(e)}")
    
    return converted, failed

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        source_dir = sys.argv[1]
        output_dir = sys.argv[2]
    else:
        source_dir = input("请输入源目录路径: ").strip().strip('"').strip("'")
        output_dir = input("请输入输出目录路径: ").strip().strip('"').strip("'")
    
    print(f"\n源目录: {source_dir}")
    print(f"输出目录: {output_dir}\n")
    
    converted, failed = convert_blog(source_dir, output_dir)
    
    print(f"\n转换完成!")
    print(f"成功: {len(converted)} 篇")
    print(f"失败: {len(failed)} 篇")
    
    if failed:
        print("\n失败列表:")
        for name, reason in failed:
            print(f"  - {name}: {reason}")
    
    input("\n按回车键退出...")