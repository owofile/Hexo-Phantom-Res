# Hexo HTML to Markdown Converter

<p align="center">
   <img src="./logo.png" alt="Logo" width="200">
</p>

<p align="center">
   <a href="./README.md">English</a> | <a href="./README.zh.md">中文</a> | <a href="./README.ja.md">日本語</a>
</p>

<p align="center">
   <img src="https://img.shields.io/badge/Python-3.8%2B-blue?logo=python" alt="Python">
   <img src="https://img.shields.io/badge/Beautiful_Soup-4.0+-green" alt="Beautiful Soup">
   <img src="https://img.shields.io/badge/Markdownify-0.11.6-orange" alt="Markdownify">
   <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>



## Introduction

The Hexo HTML to Markdown Converter is a Python script that converts Hexo-generated HTML files into Markdown files. The tool provides a simple GUI interface where users can select the source directory and output directory, and then convert files with a single click. The conversion process retains article metadata such as titles, dates, and tags, and correctly handles code blocks.

## Usage Guide

### 1. Install Dependencies

Before running the tool, ensure you have installed the required Python libraries:

```bash
pip install beautifulsoup4 markdownify
```

### 2. Download the Script

You can download the `Hexo Phantom Res.py` script from GitHub or any other code hosting platform.

### 3. Run the Script

Make sure you have installed the required dependencies, then run the script:

```bash
python Hexo Phantom Res.py
```

### 4. Use the GUI Interface

1. **Select Source Directory**:
   - Click the "Select Source Folder" button to choose the directory containing Hexo-generated HTML files.
   - The script will automatically find all `index.html` files in the directory and its subdirectories.
2. **Select Output Directory**:
   - Click the "Select Output Location" button to choose the directory where the converted Markdown files will be saved.
3. **Start Conversion**:
   - Click the "Start Conversion" button to begin converting HTML files to Markdown files.
   - A progress bar will display the conversion progress, and the log area will record the status of each step.

### 5. View the Results

After the conversion is complete, you can find the generated Markdown files in the specified output directory.

## Example

Assume your source directory structure is as follows:

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

Running the script and selecting the above source and output directories will save the generated Markdown files in the output directory, with filenames `hexo.md` and `newblog.md`.

## Notes

- **Source Directory**: Ensure the source directory contains Hexo-generated HTML files with the filename `index.html`.
- **Output Directory**: Ensure the output directory exists, or the script has permission to create new directories.
- **Code Block Handling**: The tool automatically handles Hexo's highlight code blocks and other regular code blocks, ensuring code is correctly displayed in the output.

## Contact

If you encounter any issues while using the tool, feel free to contact us via:

- **GitHub Issues**: [Submit an Issue](https://github.com/NANAFREE/Hexo-Phantom-Res/issues)

We hope this tool helps you convert Hexo-generated HTML files into Markdown files smoothly! If you have any suggestions or improvements, please let us know.