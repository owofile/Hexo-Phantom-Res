import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from bs4 import BeautifulSoup
import markdownify
import re
import os
import sys

def convert_html_to_markdown(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 提取Front Matter头部信息
    title = soup.find('h1', class_='posttitle').get_text(strip=True) if soup.find('h1', class_='posttitle') else 'Untitled'
    date_element = soup.find('time', {'class': 'dt-published'})
    date = date_element['datetime'] if date_element else ''
    tags = [tag.get_text(strip=True) for tag in soup.find_all('a', class_='p-category', rel='tag')]
    
    # 构建YAML Front Matter
    front_matter = "---\n"
    front_matter += f"title: {title}\n"
    front_matter += f"date: {date}\n"
    if tags:
        front_matter += f"tags: [{', '.join(tags)}]\n"
    front_matter += "---\n\n"
    
    # 提取文章主体 - 增强兼容性，尝试多种选择器
    article = None
    # 尝试多种常见的文章容器选择器
    article_selectors = [
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
            article = soup.find(selector['tag'], class_=selector['class'])
        elif selector.get('attrs'):
            article = soup.find(selector['tag'], attrs=selector['attrs'])
        else:
            article = soup.find(selector['tag'])
            
        if article:
            break
    
    if not article:
        log_text.insert(tk.END, "错误: 未找到文章主体\n")
        return None
    
    # 清理导航栏、页脚等无关元素
    for element in article.find_all(['header', 'footer', 'div', 'span', 'ul', 'li']):
        if element.find_parents(['header', 'footer', 'nav']):
            element.decompose()
    
    # 处理Hexo的highlight代码块
    for figure in article.find_all('figure', class_='highlight'):
        language_classes = [cls for cls in figure.get('class', []) if cls != 'highlight']
        language = language_classes[0] if language_classes else ''
        
        code_lines = []
        pre = figure.find('pre')
        if pre:
            for line in pre.find_all('span', class_='line'):
                code_lines.append(line.get_text().replace('\n', ''))
            code_content = '\n'.join(code_lines)
            code_block = f"\n```{language}\n{code_content}\n```\n"
            figure.replace_with(code_block)
    
    # 处理常规pre代码块
    for pre in article.find_all('pre'):
        if pre.find_parent('figure', class_='highlight'):
            continue
            
        code = pre.find('code')
        if code:
            language = ''
            for cls in code.get('class', []):
                if cls.startswith('language-'):
                    language = cls.split('-')[1]
                    break
            code_block = f"\n```{language}\n{code.get_text()}\n```\n"
            pre.replace_with(code_block)
        else:
            pre.replace_with(f"\n```\n{pre.get_text()}\n```\n")
    
    # 转换剩余HTML为Markdown
    markdown_body = markdownify.markdownify(str(article), heading_style="ATX")
    full_markdown = front_matter + re.sub(r'\n{3,}', '\n\n', markdown_body.strip())
    return full_markdown

def select_source_directory():
    source_dir = filedialog.askdirectory()
    if source_dir:
        source_entry.delete(0, tk.END)
        source_entry.insert(0, source_dir)

def select_output_directory():
    output_dir = filedialog.askdirectory()
    if output_dir:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, output_dir)

def start_conversion():
    source_dir = source_entry.get()
    output_dir = output_entry.get()
    
    if not source_dir or not output_dir:
        messagebox.showerror("错误", "请选择源目录和输出目录")
        return
    
    log_text.delete(1.0, tk.END)
    progress_bar['value'] = 0
    root.update_idletasks()
    status_label.config(text="正在扫描目录…")
    
    ignore_folders = {"about", "archives", "css", "friends", "images", "jpg", "js", "lib", "page", "png", "tags"}
    html_files = []
    
    for root_dir, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in ignore_folders]
        for file in files:
            if file == "index.html":
                html_files.append(os.path.join(root_dir, file))

    total_files = len(html_files)
    if total_files == 0:
        log_text.insert(tk.END, "未找到任何index.html文件\n")
        status_label.config(text="未检测到可转换页面")
        return

    status_label.config(text=f"开始转换，共 {total_files} 篇")
    for i, html_file in enumerate(html_files):
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html = f.read()

            md_content = convert_html_to_markdown(html)
            if md_content:
                folder_name = os.path.basename(os.path.dirname(html_file))
                md_file_path = os.path.join(output_dir, f"{folder_name}.md")
                
                with open(md_file_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                
                log_text.insert(tk.END, f"转换完成: {folder_name}.md\n")
            else:
                log_text.insert(tk.END, f"未找到文章主题: {html_file}\n")
                
        except Exception as e:
            log_text.insert(tk.END, f"转换失败: {html_file} - {str(e)}\n")

        log_text.see(tk.END)
        root.update_idletasks()
        progress_bar['value'] = (i + 1) / total_files * 100
        status_label.config(text=f"进度 {i + 1}/{total_files}")

    status_label.config(text="转换完成，Markdown 已生成")

def main():
    global source_entry, output_entry, log_text, progress_bar, root, status_label
    
    try:
        # 创建主窗口并设置尺寸
        root = tk.Tk()
        root.title("Hexo HTML转Markdown")
        root.geometry("900x620")
        root.minsize(780, 520)
        root.resizable(True, True)

        # 色板与字体
        palette = {
            'bg': '#f4f5f7',
            'surface': '#ffffff',
            'surface_alt': '#f9fafb',
            'border': '#e3e6ef',
            'accent': '#2563eb',
            'accent_dark': '#1d4ed8',
            'muted': '#6b7280',
            'text': '#1f2933'
        }

        if sys.platform.startswith('darwin'):
            base_font = 'SF Pro Display'
        elif sys.platform.startswith('win32'):
            base_font = 'Bahnschrift'
        else:
            base_font = 'Ubuntu'

        body_font = (base_font, 11)
        small_font = (base_font, 10)
        title_font = (base_font, 20, 'bold')
        accent_font = (base_font, 11, 'bold')

        # 设置主题与全局样式
        style = ttk.Style()
        theme = 'aqua' if sys.platform.startswith('darwin') else 'clam'
        style.theme_use(theme)

        root.configure(bg=palette['bg'])
        style.configure('.', background=palette['bg'], foreground=palette['text'], font=body_font)
        style.configure('TFrame', background=palette['bg'])
        style.configure('Card.TFrame', background=palette['surface'], relief='flat')
        style.configure('CardInner.TFrame', background=palette['surface_alt'], relief='flat')
        style.configure('Title.TLabel', background=palette['bg'], foreground=palette['text'], font=title_font)
        style.configure('Subtitle.TLabel', background=palette['bg'], foreground=palette['muted'], font=small_font)
        style.configure('CardTitle.TLabel', background=palette['surface'], foreground=palette['text'], font=(base_font, 13, 'bold'))
        style.configure('CardSubtitle.TLabel', background=palette['surface'], foreground=palette['muted'], font=small_font)
        style.configure('Accent.TButton', background=palette['accent'], foreground='#ffffff', padding=(18, 10), font=accent_font)
        style.map('Accent.TButton', background=[('active', palette['accent_dark']), ('disabled', palette['border'])])
        style.configure('Ghost.TButton', background=palette['surface'], foreground=palette['accent'], padding=(12, 8))
        style.map('Ghost.TButton', background=[('active', palette['surface_alt'])], foreground=[('active', palette['accent_dark'])])
        style.configure('Accent.Horizontal.TProgressbar', background=palette['accent'], troughcolor=palette['surface_alt'], bordercolor=palette['surface_alt'])

        # 主容器
        main_frame = ttk.Frame(root, padding=30)
        main_frame.pack(fill='both', expand=True)
        main_frame.columnconfigure(0, weight=1)

        # 顶部信息卡片
        hero_card = ttk.Frame(main_frame, style='Card.TFrame', padding=24)
        hero_card.grid(row=0, column=0, sticky='ew')

        ttk.Label(hero_card, text="Hexo HTML 转 Markdown", style='Title.TLabel').pack(anchor='w')
        ttk.Label(
            hero_card,
            text="批量将已部署的 Hexo 文章恢复为 Markdown，并自动补齐 Front Matter。",
            style='Subtitle.TLabel',
            wraplength=720,
            padding=(0, 8, 0, 0)
        ).pack(anchor='w')

        # 目录设置卡片
        directory_card = ttk.Frame(main_frame, style='Card.TFrame', padding=24)
        directory_card.grid(row=1, column=0, sticky='ew', pady=(20, 0))
        directory_card.columnconfigure(1, weight=1)

        ttk.Label(directory_card, text="工作目录", style='CardTitle.TLabel').grid(row=0, column=0, columnspan=3, sticky='w')
        ttk.Label(
            directory_card,
            text="指定 Hexo 生成的静态站点位置以及导出的 Markdown 保存位置。",
            style='CardSubtitle.TLabel'
        ).grid(row=1, column=0, columnspan=3, sticky='w', pady=(4, 16))

        ttk.Label(directory_card, text="源目录", font=body_font, background=palette['surface']).grid(row=2, column=0, sticky='w')
        source_entry = ttk.Entry(directory_card, font=small_font)
        source_entry.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(6, 18), padx=(0, 10))
        ttk.Button(directory_card, text="浏览", style='Ghost.TButton', command=select_source_directory).grid(row=3, column=2, sticky='e')

        ttk.Label(directory_card, text="输出目录", font=body_font, background=palette['surface']).grid(row=4, column=0, sticky='w')
        output_entry = ttk.Entry(directory_card, font=small_font)
        output_entry.grid(row=5, column=0, columnspan=2, sticky='ew', pady=(6, 0), padx=(0, 10))
        ttk.Button(directory_card, text="浏览", style='Ghost.TButton', command=select_output_directory).grid(row=5, column=2, sticky='e')

        # 操作卡片
        action_card = ttk.Frame(main_frame, style='Card.TFrame', padding=24)
        action_card.grid(row=2, column=0, sticky='ew', pady=(20, 0))
        action_card.columnconfigure(0, weight=1)

        ttk.Label(action_card, text="准备完成即可一键转换", style='CardTitle.TLabel').grid(row=0, column=0, sticky='w')
        ttk.Label(
            action_card,
            text="转换过程中不会修改原始文件，仅在目标目录写入 Markdown。",
            style='CardSubtitle.TLabel'
        ).grid(row=1, column=0, sticky='w', pady=(4, 18))

        ttk.Button(action_card, text="开始转换", style='Accent.TButton', command=start_conversion).grid(row=2, column=0, sticky='e')

        # 日志与进度
        log_card = ttk.Frame(main_frame, style='Card.TFrame', padding=24)
        log_card.grid(row=3, column=0, sticky='nsew', pady=(20, 0))
        main_frame.rowconfigure(3, weight=1)

        ttk.Label(log_card, text="转换日志", style='CardTitle.TLabel').pack(anchor='w')
        status_label = ttk.Label(log_card, text="等待操作", style='CardSubtitle.TLabel')
        status_label.pack(anchor='w', pady=(2, 12))

        log_text = tk.Text(
            log_card,
            height=8,
            font=small_font,
            wrap='word',
            bd=0,
            highlightthickness=0,
            bg=palette['surface_alt'],
            fg=palette['text'],
            relief='flat',
            insertbackground=palette['accent']
        )
        log_text.pack(fill='both', expand=True, pady=(0, 16))

        progress_bar = ttk.Progressbar(log_card, orient="horizontal", mode="determinate", style='Accent.Horizontal.TProgressbar')
        progress_bar.pack(fill='x')
        
        root.mainloop()
        
    except Exception as e:
        # 错误处理窗口
        error_root = tk.Tk()
        error_root.title("启动错误")
        error_root.geometry("400x150")
        
        error_frame = ttk.Frame(error_root, padding=20)
        error_frame.pack(fill='both', expand=True)
        
        # 根据系统选择合适字体
        if sys.platform.startswith('darwin'):
            error_font = ('-apple-system', 10)
        elif sys.platform.startswith('win32'):
            error_font = ('Segoe UI', 10)
        else:
            error_font = ('Ubuntu', 10)
            
        ttk.Label(
            error_frame, 
            text=f"程序启动失败:\n{str(e)}", 
            wraplength=350,
            font=error_font
        ).pack(anchor='w', pady=(0, 15))
        
        ttk.Button(
            error_frame, 
            text="确定", 
            command=error_root.quit,
            width=10
        ).pack(anchor='e')
        
        error_root.mainloop()

if __name__ == "__main__":
    main()
