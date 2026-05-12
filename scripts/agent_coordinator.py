"""
Hexo-Phantom-Res Multi-Agent Coordinator

This script coordinates multiple agents to analyze and convert Hexo HTML to Markdown.
It uses a task-based approach where different agents handle different aspects:
1. Analyzer agent - Analyzes HTML structure
2. Converter agent - Performs the actual conversion
3. Validator agent - Validates output quality

Usage:
    python agent_coordinator.py <source_dir> <output_dir> [--analyze-only] [--validate]
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}\n")

def print_status(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

class AnalyzerAgent:
    """Analyzes HTML structure to determine the best extraction strategy"""
    
    def __init__(self, sample_files):
        self.sample_files = sample_files
        self.theme_patterns = {
            'redefine': {
                'article_container': ['article-content', 'markdown-body'],
                'code_container': 'code-container',
                'code_elem': 'td.code',
                'line_span': 'span.line',
                'lang_attr': 'data-rel'
            },
            'next': {
                'article_container': ['post-content', 'article-content'],
                'code_container': 'figure.highlight',
                'code_elem': 'td.code',
                'line_span': 'span.line',
                'lang_in': 'figure'
            },
            'icarus': {
                'article_container': ['article', 'post-content'],
                'code_container': 'div.highlight',
                'code_elem': 'pre',
                'line_span': None,
                'lang_in': 'code'
            }
        }
    
    def analyze(self):
        """Analyze HTML files and determine theme type"""
        from bs4 import BeautifulSoup
        
        print_status("Analyzer agent: Starting HTML structure analysis...")
        
        results = []
        for file_path in self.sample_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    html = f.read()
                
                soup = BeautifulSoup(html, 'html.parser')
                analysis = {
                    'file': os.path.basename(os.path.dirname(file_path)),
                    'article_containers': [],
                    'code_containers': 0,
                    'code_format': None,
                    'language_detection': None,
                    'likely_theme': 'unknown'
                }
                
                for cls in ['article-content', 'markdown-body', 'post-content', 'entry-content', 'post']:
                    elem = soup.find(class_=lambda c: c and cls in c if isinstance(c, str) else False)
                    if elem:
                        analysis['article_containers'].append(cls)
                
                code_containers = soup.find_all('div', class_='code-container')
                figures = soup.find_all('figure', class_=lambda c: 'highlight' in c if c else False)
                analysis['code_containers'] = len(code_containers) + len(figures)
                
                if code_containers:
                    sample = code_containers[0]
                    if sample.get('data-rel'):
                        analysis['code_format'] = 'code-container-data-rel'
                        analysis['language_detection'] = f"data-rel={sample.get('data-rel')}"
                elif figures:
                    sample = figures[0]
                    lang_classes = [c for c in sample.get('class', []) if c not in ('highlight', 'iseeu')]
                    if lang_classes:
                        analysis['code_format'] = 'figure-class'
                        analysis['language_detection'] = f"class={lang_classes[0]}"
                
                if analysis['article_containers'] and analysis['code_containers'] > 0:
                    if 'article-content' in analysis['article_containers']:
                        analysis['likely_theme'] = 'redefine'
                    elif 'post-content' in analysis['article_containers']:
                        analysis['likely_theme'] = 'next'
                
                results.append(analysis)
                print_status(f"  - {analysis['file']}: theme={analysis['likely_theme']}, code_blocks={analysis['code_containers']}")
                
            except Exception as e:
                print_status(f"  - Error analyzing {file_path}: {e}")
        
        return results

class ConverterAgent:
    """Performs the actual HTML to Markdown conversion"""
    
    def __init__(self, config):
        self.config = config
        self.ignore_folders = {"about", "archives", "css", "friends", "images", "jpg", "js", "lib", "page", "png", "tags"}
    
    def convert(self, source_dir, output_dir, theme_config=None):
        """Convert all HTML files in source to Markdown"""
        from bs4 import BeautifulSoup
        import markdownify
        import re
        
        print_status("Converter agent: Starting conversion...")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if theme_config is None:
            theme_config = self._get_default_config()
        
        converted = []
        failed = []
        
        total = sum(1 for root, dirs, files in os.walk(source_dir)
                   for f in files if f == 'index.html')
        
        current = 0
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in self.ignore_folders]
            
            for file in files:
                if file != 'index.html':
                    continue
                
                current += 1
                html_path = os.path.join(root, file)
                folder_name = os.path.basename(root)
                
                try:
                    with open(html_path, 'r', encoding='utf-8') as f:
                        html = f.read()
                    
                    md = self._convert_single(html, theme_config)
                    if md:
                        output_path = os.path.join(output_dir, f"{folder_name}.md")
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(md)
                        converted.append(folder_name)
                        print_status(f"  [{current}/{total}] OK: {folder_name}.md")
                    else:
                        failed.append((folder_name, 'Conversion returned None'))
                        print_status(f"  [{current}/{total}] FAIL: {folder_name} - Conversion returned None")
                        
                except Exception as e:
                    failed.append((folder_name, str(e)))
                    print_status(f"  [{current}/{total}] FAIL: {folder_name} - {str(e)}")
        
        return converted, failed
    
    def _convert_single(self, html, config):
        """Convert a single HTML file to Markdown"""
        from bs4 import BeautifulSoup
        import markdownify
        import re
        
        soup = BeautifulSoup(html, 'html.parser')
        
        title_elem = soup.find('h1', class_=re.compile(r'article-title-regular|posttitle'))
        if not title_elem:
            title_elem = soup.find('meta', property='og:title')
        title = title_elem.get_text(strip=True) if title_elem else title_elem.get('content', 'Untitled') if title_elem else 'Untitled'
        
        date = ''
        date_elem = soup.find('time', {'class': 'dt-published'})
        if date_elem:
            date = date_elem.get('datetime', '')[:19].replace('T', ' ')
        else:
            meta_date = soup.find('meta', property='article:published_time')
            if meta_date:
                date = meta_date.get('content', '')[:19].replace('T', ' ')
        
        tags = []
        for tag in soup.find_all('a', href=lambda h: h and '/tags/' in h):
            tag_text = tag.get_text(strip=True).lstrip('#')
            if tag_text and tag_text not in tags:
                tags.append(tag_text)
        
        front_matter = f"---\ntitle: {title}\ndate: {date}\n"
        if tags:
            front_matter += f"tags: [{', '.join(tags)}]\n"
        front_matter += "---\n\n"
        
        article = soup.find('div', class_=re.compile(r'article-content|markdown-body'))
        if not article:
            article = soup.find('article', class_=re.compile(r'post'))
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
        
        markdown_body = markdownify.markdownify(str(article), heading_style="ATX", 
                                               links_callback=lambda href, text: href if href and not href.startswith('/blog/tags') else None)
        
        return front_matter + re.sub(r'\n{3,}', '\n\n', markdown_body.strip())
    
    def _get_default_config(self):
        return {
            'article_containers': ['article-content', 'markdown-body', 'post-content', 'article'],
            'code_container': 'code-container',
            'code_elem': 'td.code',
            'line_span': 'span.line',
            'lang_source': 'data-rel'
        }

class ValidatorAgent:
    """Validates converted Markdown files"""
    
    def __init__(self):
        pass
    
    def validate(self, output_dir):
        """Validate converted Markdown files"""
        print_status("Validator agent: Starting validation...")
        
        results = []
        issues = []
        
        for filename in os.listdir(output_dir):
            if not filename.endswith('.md'):
                continue
            
            filepath = os.path.join(output_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                validation = {
                    'file': filename,
                    'has_front_matter': False,
                    'has_title': False,
                    'has_date': False,
                    'has_content': False,
                    'code_blocks': 0,
                    'issues': []
                }
                
                if content.startswith('---'):
                    validation['has_front_matter'] = True
                    
                    if '\ntitle:' in content:
                        validation['has_title'] = True
                    if '\ndate:' in content:
                        validation['has_date'] = True
                
                if '---' in content:
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        body = parts[2].strip()
                        if len(body) > 100:
                            validation['has_content'] = True
                        
                        validation['code_blocks'] = body.count('```')
                
                if not validation['has_front_matter']:
                    validation['issues'].append('Missing front matter')
                if not validation['has_title']:
                    validation['issues'].append('Missing title in front matter')
                if not validation['has_date']:
                    validation['issues'].append('Missing date in front matter')
                if not validation['has_content']:
                    validation['issues'].append('Content appears empty')
                
                results.append(validation)
                
                if validation['issues']:
                    issues.extend([(filename, issue) for issue in validation['issues']])
                    print_status(f"  - {filename}: {len(validation['issues'])} issues")
                else:
                    print_status(f"  - {filename}: OK")
                    
            except Exception as e:
                issues.append((filename, f"Validation error: {str(e)}"))
                print_status(f"  - {filename}: ERROR - {str(e)}")
        
        return results, issues

def run_coordinator(source_dir, output_dir, analyze_only=False, validate=True):
    """Main coordinator function"""
    
    print_section("Hexo-Phantom-Res Multi-Agent Coordinator")
    
    print_status(f"Source: {source_dir}")
    print_status(f"Output: {output_dir}")
    
    sample_files = []
    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in {'about', 'archives', 'css', 'friends', 'images', 'jpg', 'js', 'lib', 'page', 'png', 'tags'}]
        if 'index.html' in files:
            sample_files.append(os.path.join(root, 'index.html'))
            if len(sample_files) >= 3:
                break
    
    analyzer = AnalyzerAgent(sample_files)
    analysis_results = analyzer.analyze()
    
    theme_config = None
    if analysis_results:
        most_common_theme = max(set([r['likely_theme'] for r in analysis_results]), 
                                key=lambda x: sum(1 for r in analysis_results if r['likely_theme'] == x))
        print_status(f"Detected theme: {most_common_theme}")
    
    if analyze_only:
        print_status("Analyze only mode - skipping conversion")
        return
    
    converter = ConverterAgent(theme_config)
    converted, failed = converter.convert(source_dir, output_dir, theme_config)
    
    print_status(f"Conversion complete: {len(converted)} success, {len(failed)} failed")
    
    if validate and converted:
        validator = ValidatorAgent()
        validation_results, issues = validator.validate(output_dir)
        
        valid_count = sum(1 for r in validation_results if not r['issues'])
        print_status(f"Validation complete: {valid_count}/{len(validation_results)} valid")
        
        if issues:
            print_status(f"Found {len(issues)} issues to review")
    
    print_section("Summary")
    print(f"Converted: {len(converted)} files")
    print(f"Failed: {len(failed)} files")
    
    if failed:
        print("\nFailed files:")
        for name, reason in failed:
            print(f"  - {name}: {reason}")

def main():
    parser = argparse.ArgumentParser(description='Hexo-Phantom-Res Multi-Agent Coordinator')
    parser.add_argument('source_dir', nargs='?', help='Source directory containing Hexo HTML files')
    parser.add_argument('output_dir', nargs='?', help='Output directory for Markdown files')
    parser.add_argument('--analyze-only', action='store_true', help='Only analyze HTML structure, do not convert')
    parser.add_argument('--validate', action='store_true', default=True, help='Validate output after conversion')
    
    args = parser.parse_args()
    
    if not args.source_dir or not args.output_dir:
        print("Usage: python agent_coordinator.py <source_dir> <output_dir> [--analyze-only] [--validate]")
        print("\nOr enter paths interactively:")
        source = input("Source directory: ").strip().strip('"').strip("'")
        output = input("Output directory: ").strip().strip('"').strip("'")
        args.source_dir = source
        args.output_dir = output
    
    if not os.path.exists(args.source_dir):
        print(f"Error: Source directory does not exist: {args.source_dir}")
        return
    
    run_coordinator(args.source_dir, args.output_dir, args.analyze_only, args.validate)

if __name__ == "__main__":
    main()