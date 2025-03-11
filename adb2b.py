'''
Author: Diana Tang
Date: 2025-03-11 20:09:34
LastEditors: Diana Tang
Description: some description
FilePath: /express-pdf/adb2b.py
'''
#!/usr/bin/env python3
"""
将books目录下的所有PDF文件压缩后输出到eBooks目录
使用高级压缩方法

使用方法: python books_to_ebooks_advanced.py [压缩方法]

压缩方法选项:
- advanced-gs：使用高级Ghostscript设置（默认）
- qpdf：使用QPDF工具
- img2pdf：转换为图像后重建PDF（文件最小但可能影响文本选择）
- ocrmypdf：OCR处理（适合扫描文档）
- all：尝试所有方法并选择最佳结果（推荐但较慢）
"""

import os
import sys
import logging
from pathlib import Path

# 导入高级PDF压缩模块
from adMain import process_directory

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # 确定项目的根目录
    script_dir = Path(__file__).parent.absolute()
    
    # 设置输入和输出目录
    books_dir = script_dir / "books"
    ebooks_dir = script_dir / "eBooks"
    
    # 检查books目录是否存在
    if not books_dir.exists():
        logger.error(f"错误: 未找到books目录: {books_dir}")
        logger.info("请确保books目录存在并包含PDF文件")
        return
    
    # 确保eBooks目录存在
    ebooks_dir.mkdir(exist_ok=True)
    
    # 获取压缩方法参数
    method = "advanced-gs"  # 默认方法
    if len(sys.argv) > 1 and sys.argv[1] in ["advanced-gs", "qpdf", "img2pdf", "ocrmypdf", "all"]:
        method = sys.argv[1]
    
    # 获取DPI参数（仅用于img2pdf方法）
    dpi = 150  # 默认DPI
    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        dpi = int(sys.argv[2])
    
    logger.info(f"正在将books目录下的PDF文件压缩到eBooks目录")
    logger.info(f"使用压缩方法: {method}" + (f", DPI: {dpi}" if method == "img2pdf" else ""))
    
    # 显示依赖提示
    show_dependencies_info(method)
    
    # 调用process_directory函数处理整个目录
    process_directory(str(books_dir), str(ebooks_dir), method, dpi, verbose=True)
    
    logger.info("\n处理完成! 压缩文件已保存到eBooks目录")

def show_dependencies_info(method):
    """显示所需依赖信息"""
    dependencies = {
        "advanced-gs": ["Ghostscript (gs)"],
        "qpdf": ["QPDF"],
        "img2pdf": ["pdftoppm (poppler-utils)", "img2pdf"],
        "ocrmypdf": ["OCRmyPDF", "Tesseract"]
    }
    
    if method == "all":
        logger.info("注意: 'all'方法将尝试所有可用的压缩方法")
        logger.info("所需依赖:")
        for dep_list in dependencies.values():
            for dep in dep_list:
                logger.info(f"  - {dep}")
    else:
        if method in dependencies:
            logger.info("所需依赖:")
            for dep in dependencies[method]:
                logger.info(f"  - {dep}")

if __name__ == "__main__":
    main()