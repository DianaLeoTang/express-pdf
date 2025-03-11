'''
Author: Diana Tang
Date: 2025-03-11 18:43:16
LastEditors: Diana Tang
Description: some description
FilePath: /AI-Health-News-Agent-Back/b2b.py
'''
#!/usr/bin/env python3
"""
将books目录下的所有PDF文件压缩后输出到eBooks目录
使用方法: python books_to_ebooks.py [质量选项]
"""

import os
import sys
import subprocess
from pathlib import Path

# 导入PDF压缩模块
from main import process_directory

def main():
    # 确定项目的根目录
    script_dir = Path(__file__).parent.absolute()
    
    # 设置输入和输出目录
    books_dir = script_dir / "books"
    ebooks_dir = script_dir / "eBooks"
    
    # 检查books目录是否存在
    if not books_dir.exists():
        print(f"错误: 未找到books目录: {books_dir}")
        print("请确保books目录存在并包含PDF文件")
        return
    
    # 确保eBooks目录存在
    ebooks_dir.mkdir(exist_ok=True)
    
    # 获取压缩质量参数
    quality = "printer"  # 默认质量
    if len(sys.argv) > 1 and sys.argv[1] in ["screen", "ebook", "printer", "prepress", "default"]:
        quality = sys.argv[1]
    
    print(f"正在将books目录下的PDF文件压缩到eBooks目录 (质量: {quality})")
    
    # 调用process_directory函数处理整个目录
    process_directory(str(books_dir), str(ebooks_dir), quality, verbose=True)
    
    print("\n处理完成! 压缩文件已保存到eBooks目录")

if __name__ == "__main__":
    main()