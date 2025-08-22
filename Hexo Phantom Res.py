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
    
    # 提取文章主体
    article = soup.find('article', class_='post')
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
        return
    
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

def main():
    global source_entry, output_entry, log_text, progress_bar, root
    
    try:
        # 创建主窗口并设置更小的尺寸
        root = tk.Tk()
        root.title("Hexo HTML转Markdown")
        root.geometry("700x500")  # 窗口尺寸从800x550调整为700x500
        root.resizable(True, True)  # 允许调整窗口大小
        
        # 设置主题 - 跨平台兼容
        style = ttk.Style()
        if sys.platform.startswith('darwin'):  # macOS系统
            style.theme_use('aqua')  # 使用macOS原生主题
        else:
            style.theme_use('clam')  # Windows和Linux使用clam主题
        
        # 跨平台字体设置
        if sys.platform.startswith('darwin'):  # macOS
            default_font = ('-apple-system', 10)
        elif sys.platform.startswith('win32'):  # Windows
            default_font = ('Segoe UI', 10)
        else:  # Linux
            default_font = ('Ubuntu', 10)
            
        font_entry = (default_font[0], 9)
        font_button = (default_font[0], 10, 'bold')
        
        # 主容器，使用padding创建留白
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # 标题标签
        title_label = ttk.Label(
            main_frame, 
            text="Hexo HTML 转 Markdown", 
            font=(default_font[0], 14, 'bold')
        )
        title_label.pack(anchor='w', pady=(0, 15))  # 减少标题下方间距
        
        # 添加分隔线增强视觉层次
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill='x', pady=(0, 15))
        
        # 目录选择区域 - 优化布局
        directory_frame = ttk.Frame(main_frame)
        directory_frame.pack(fill='x', pady=(0, 15))
        
        # 源目录选择
        ttk.Label(directory_frame, text="源目录:", font=default_font).grid(row=0, column=0, sticky='w', pady=3)
        source_entry = ttk.Entry(directory_frame, font=font_entry)
        source_entry.grid(row=1, column=0, sticky='ew', padx=(0, 10), pady=2)
        ttk.Button(
            directory_frame, 
            text="浏览...", 
            command=select_source_directory,
            width=8  # 统一按钮宽度
        ).grid(row=1, column=1, sticky='w', pady=2)
        
        # 输出目录选择
        ttk.Label(directory_frame, text="输出目录:", font=default_font).grid(row=2, column=0, sticky='w', pady=3)
        output_entry = ttk.Entry(directory_frame, font=font_entry)
        output_entry.grid(row=3, column=0, sticky='ew', padx=(0, 10), pady=2)
        ttk.Button(
            directory_frame, 
            text="浏览...", 
            command=select_output_directory,
            width=8  # 统一按钮宽度
        ).grid(row=3, column=1, sticky='w', pady=2)
        
        # 设置列权重，使输入框自适应宽度
        directory_frame.columnconfigure(0, weight=1)
        
        # 转换按钮 - 优化样式和位置
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(0, 15))
        
        convert_button = ttk.Button(
            button_frame, 
            text="开始转换", 
            command=start_conversion,
            width=15
        )
        convert_button.pack(anchor='e')  # 按钮右对齐
        
        # 日志和进度区域 - 优化比例
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill='both', expand=True)
        
        # 日志标题
        ttk.Label(log_frame, text="转换日志:", font=default_font).pack(anchor='w')
        
        # 日志文本框 - 优化高度
        log_text = tk.Text(
            log_frame, 
            height=7,  # 调整日志区域高度
            font=font_entry,
            wrap='word',
            bd=1, 
            relief='solid',
            highlightthickness=0
        )
        log_text.pack(fill='both', expand=True, pady=(5, 10))
        
        # 进度条
        progress_bar = ttk.Progressbar(log_frame, orient="horizontal", length=100, mode="determinate")
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