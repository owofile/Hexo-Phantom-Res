import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from bs4 import BeautifulSoup
import markdownify
import re
import os

#目前BUG
#无法识别大部分文章Code，转换后有格式错误


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
        front_matter += f"tags: [{', '.join(tags)}]\n"  # 修改为单行列表格式
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
    
    # 处理Hexo的highlight代码块（包裹在<figure>中的结构）
    for figure in article.find_all('figure', class_='highlight'):
        # 从figure的class中提取语言类型（如"highlight sh" -> "sh"）
        language_classes = [cls for cls in figure.get('class', []) if cls != 'highlight']
        language = language_classes[0] if language_classes else ''
        
        # 提取所有代码行
        code_lines = []
        pre = figure.find('pre')
        if pre:
            # 处理带<span class="line">的Hexo格式
            for line in pre.find_all('span', class_='line'):
                code_lines.append(line.get_text().replace('\n', ''))  # 移除行内换行
            # 或直接获取pre的文本（根据实际HTML结构选择）
            # code_content = pre.get_text('\n').strip()
        code_content = '\n'.join(code_lines)
        
        # 生成Markdown代码块
        code_block = f"\n``{language}\n{code_content}\n```\n"
        figure.replace_with(code_block)

    # 处理常规pre代码块（非Hexo特殊结构）
    for pre in article.find_all('pre'):
        # 跳过已被figure处理过的pre
        if pre.find_parent('figure', class_='highlight'):
            continue
        
        code = pre.find('code')
        if code:
            # 原有语言提取逻辑
            language = ''
            for cls in code.get('class', []):
                if cls.startswith('language-'):
                    language = cls.split('-')[1]
                    break
            code_block = f"\n```{language}\n{code.get_text()}\n```\n"
            pre.replace_with(code_block)
        else:
            # 无语言标识的普通代码块
            pre.replace_with(f"\n```\n{pre.get_text()}\n```\n")

    # 转换剩余HTML为Markdown
    markdown_body = markdownify.markdownify(str(article), heading_style="ATX")
    
    # 合并Front Matter和正文，并清理多余空行
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
    global root  # 声明root为全局变量
    source_dir = source_entry.get()
    output_dir = output_entry.get()
    
    if not source_dir or not output_dir:
        messagebox.showerror("错误", "请选择源目录和输出目录")
        return
    
    log_text.delete(1.0, tk.END)
    progress_bar['value'] = 0
    root.update_idletasks()  # 确保root引用Tkinter主窗口对象
    
    # 增加过滤列表
    ignore_folders = {"about", "archives", "css", "friends", "images", "jpg", "js", "lib", "page", "png", "tags"}
    
    html_files = []
    for root_dir, dirs, files in os.walk(source_dir):  # 修改变量名以避免与全局root冲突
        # 过滤目录
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
                log_text.see(tk.END)
                root.update_idletasks()
                progress_bar['value'] = (i + 1) / total_files * 100
            else:
                log_text.insert(tk.END, f"未找到文章主题: {html_file}\n")
                log_text.see(tk.END)
                root.update_idletasks()
        except Exception as e:
            log_text.insert(tk.END, f"转换失败: {html_file} - {str(e)}\n")
            log_text.see(tk.END)
            root.update_idletasks()

def main():
    global source_entry, output_entry, log_text, progress_bar, root
    
    root = tk.Tk()
    root.title("Hexo HTML转Markdown工具")
    root.geometry("800x600")
    root.configure(bg='#f0f0f0')  # 设置背景颜色
    
    # 设置现代主题风格
    style = ttk.Style()
    style.theme_use('clam')
    
    # 主容器框架
    main_frame = ttk.Frame(root)
    main_frame.pack(padx=20, pady=20, fill='both', expand=True)

    # 设置现代字体
    font_label = ('微软雅黑', 10)
    font_entry = ('微软雅黑', 9)
    font_button = ('微软雅黑', 10, 'bold')
    
    # 第一部分：源目录选择
    source_frame = ttk.LabelFrame(main_frame, text=" 源目录设置 ", padding=(10, 5))
    source_frame.pack(fill='x', pady=5)
    
    ttk.Label(source_frame, text="选择源文件夹:", font=font_label).grid(row=0, column=0, sticky='w')
    source_entry = ttk.Entry(source_frame, width=50, font=font_entry)
    source_entry.grid(row=1, column=0, padx=(0, 5), sticky='ew')
    ttk.Button(source_frame, text="浏览...", command=select_source_directory, 
              style='Accent.TButton').grid(row=1, column=1, sticky='e')
    
    # 第二部分：输出目录选择
    output_frame = ttk.LabelFrame(main_frame, text=" 输出目录设置 ", padding=(10, 5))
    output_frame.pack(fill='x', pady=10)
    
    ttk.Label(output_frame, text="选择输出位置:", font=font_label).grid(row=0, column=0, sticky='w')
    output_entry = ttk.Entry(output_frame, width=50, font=font_entry)
    output_entry.grid(row=1, column=0, padx=(0, 5), sticky='ew')
    ttk.Button(output_frame, text="浏览...", command=select_output_directory, 
              style='Accent.TButton').grid(row=1, column=1, sticky='e')
    
    # 转换按钮
    btn_convert = ttk.Button(main_frame, text="开始转换", command=start_conversion, 
                            style='Accent.TButton')
    btn_convert.pack(pady=15, ipadx=20, ipady=5)

    # 日志区域
    log_frame = ttk.LabelFrame(main_frame, text=" 转换日志 ", padding=(10, 5))
    log_frame.pack(fill='both', expand=True)
    
    log_text = tk.Text(log_frame, width=70, height=10, font=font_entry, 
                      bg='#ffffff', fg='#333333', wrap='word')
    log_text.pack(fill='both', expand=True)
    
    # 进度条
    progress_bar = ttk.Progressbar(main_frame, orient="horizontal", 
                                  length=500, mode="determinate")
    progress_bar.pack(fill='x', pady=10)

    # 样式配置
    style.configure('Accent.TButton', font=font_button, 
                   foreground='white', background='#2c7be5',
                   padding=6, bordercolor='#2c7be5')
    style.map('Accent.TButton',
             foreground=[('pressed', 'white'), ('active', 'white')],
             background=[('pressed', '#1c5cb7'), ('active', '#256fd9')])
    
    # 设置列和行的权重
    source_frame.columnconfigure(0, weight=1)
    output_frame.columnconfigure(0, weight=1)
    
    root.mainloop()

if __name__ == "__main__":
    main()