import os
import argparse
from pikepdf import Pdf
import tempfile
import subprocess
import shutil


def compress_with_ghostscript(input_path, output_path, quality="printer"):
    """
    使用Ghostscript工具压缩PDF
    
    quality参数可选值:
    - screen: 屏幕质量 (72 dpi)
    - ebook: 低质量 (150 dpi)
    - printer: 打印质量 (300 dpi)
    - prepress: 高质量印刷 (300 dpi, 色彩保留)
    - default: 默认质量
    """
    quality_options = {
        "screen": "/screen",
        "ebook": "/ebook",
        "printer": "/printer",
        "prepress": "/prepress",
        "default": "/default"
    }
    
    # 确保质量选项有效
    if quality not in quality_options:
        quality = "printer"
    
    gs_command = [
        "gs", "-sDEVICE=pdfwrite", 
        f"-dPDFSETTINGS={quality_options[quality]}", 
        "-dCompatibilityLevel=1.4",
        "-dNOPAUSE", "-dQUIET", "-dBATCH",
        f"-sOutputFile={output_path}", input_path
    ]
    
    try:
        subprocess.run(gs_command, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("警告: Ghostscript压缩失败，请确保已安装Ghostscript")
        return False


def compress_with_pikepdf(input_path, output_path, image_dpi=150):
    """使用pikepdf进行PDF压缩"""
    try:
        pdf = Pdf.open(input_path)
        
        # 减少对象副本，消除冗余
        if hasattr(pdf, 'remove_unreferenced_resources'):
            pdf.remove_unreferenced_resources()
        
        # 保存为优化格式
        pdf.save(output_path, 
                 linearize=True,    # 优化网络传输
                 compress_streams=True,  # 压缩流数据
                 recompress_flate=True,  # 重新压缩已压缩的数据
                 save_version='1.7'  # 使用现代PDF格式
                )
        return True
    except Exception as e:
        print(f"使用pikepdf压缩失败: {e}")
        return False


def compress_pdf(input_path, output_path=None, quality="printer", verbose=True):
    """
    压缩PDF文件，尝试多种方法
    
    参数:
    - input_path: 输入PDF路径
    - output_path: 输出PDF路径 (如果为None，则覆盖原文件)
    - quality: 压缩质量，可选 "screen", "ebook", "printer", "prepress", "default"
    - verbose: 是否显示详细信息
    
    返回:
    - 成功与否
    - 压缩率信息
    """
    if not os.path.exists(input_path):
        print(f"错误: 找不到文件 {input_path}")
        return False, None
    
    # 获取原始文件大小
    original_size = os.path.getsize(input_path)
    
    # 如果没有指定输出路径，创建临时文件
    is_temp = False
    if output_path is None:
        is_temp = True
        temp_fd, output_path = tempfile.mkstemp(suffix=".pdf")
        os.close(temp_fd)
    
    # 尝试使用Ghostscript压缩 (通常效果最好)
    gs_success = compress_with_ghostscript(input_path, output_path, quality)
    
    # 如果Ghostscript失败，尝试pikepdf
    if not gs_success:
        pikepdf_success = compress_with_pikepdf(input_path, output_path)
        if not pikepdf_success:
            print("错误: 所有压缩方法均失败")
            if is_temp:
                os.remove(output_path)
            return False, None
    
    # 获取压缩后的文件大小
    compressed_size = os.path.getsize(output_path)
    
    # 如果压缩后文件大于原始文件，不采用压缩结果
    if compressed_size >= original_size:
        if verbose:
            print("压缩未能减小文件大小，保持原始文件")
        if is_temp:
            os.remove(output_path)
        return False, None
    
    # 计算压缩率
    compression_ratio = (1 - compressed_size / original_size) * 100
    
    if verbose:
        print(f"原始大小: {original_size / 1024:.2f} KB")
        print(f"压缩后大小: {compressed_size / 1024:.2f} KB")
        print(f"压缩率: {compression_ratio:.2f}%")
    
    # 如果是临时文件，替换原始文件
    if is_temp:
        shutil.move(output_path, input_path)
        return True, compression_ratio
    
    return True, compression_ratio


def process_directory(input_dir, output_dir, quality="printer", verbose=True):
    """
    处理整个目录的PDF文件
    
    参数:
    - input_dir: 输入目录路径
    - output_dir: 输出目录路径
    - quality: 压缩质量
    - verbose: 是否显示详细信息
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有PDF文件
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"在 {input_dir} 中未找到PDF文件")
        return
    
    total_files = len(pdf_files)
    success_count = 0
    total_saved = 0
    
    if verbose:
        print(f"找到 {total_files} 个PDF文件需要处理")
    
    for i, pdf_file in enumerate(pdf_files, 1):
        input_path = os.path.join(input_dir, pdf_file)
        output_path = os.path.join(output_dir, pdf_file)
        
        if verbose:
            print(f"\n处理 [{i}/{total_files}]: {pdf_file}")
        
        success, compression_ratio = compress_pdf(input_path, output_path, quality, verbose)
        
        if success:
            success_count += 1
            if compression_ratio:
                original_size = os.path.getsize(input_path) / 1024
                compressed_size = os.path.getsize(output_path) / 1024
                saved_kb = original_size - compressed_size
                total_saved += saved_kb
    
    if verbose:
        print(f"\n压缩完成: {success_count}/{total_files} 文件成功压缩")
        print(f"总共节省: {total_saved:.2f} KB")


def main():
    parser = argparse.ArgumentParser(description="PDF文件压缩工具")
    parser.add_argument("input", help="输入PDF文件路径或目录路径")
    parser.add_argument("-o", "--output", help="输出PDF文件路径或目录路径 (默认覆盖原文件)")
    parser.add_argument(
        "-q", "--quality", 
        choices=["screen", "ebook", "printer", "prepress", "default"],
        default="printer",
        help="压缩质量 (默认: printer)"
    )
    parser.add_argument("--silent", action="store_true", help="静默模式，不显示详细信息")
    parser.add_argument("--batch", action="store_true", help="批处理模式，处理整个目录")
    
    args = parser.parse_args()
    
    # 批处理模式，处理整个目录
    if args.batch or os.path.isdir(args.input):
        if not args.output:
            print("错误: 批处理模式下必须指定输出目录")
            return
        process_directory(args.input, args.output, args.quality, not args.silent)
    else:
        # 单文件模式
        compress_pdf(args.input, args.output, args.quality, not args.silent)


if __name__ == "__main__":
    main()