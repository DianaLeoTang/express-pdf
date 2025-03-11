import os
import argparse
import subprocess
import shutil
from pathlib import Path
import tempfile
import logging
import sys

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def compress_with_gs_high_quality(input_path, output_path):
    """
    使用Ghostscript高级配置进行高质量压缩
    这种方法比标准预设提供更好的控制
    """
    gs_command = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dPDFA=2",
        "-dCompatibilityLevel=1.5",
        "-dPDFSETTINGS=/printer",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        "-dDetectDuplicateImages=true",
        "-dCompressFonts=true",
        "-dSubsetFonts=true",
        "-dCompressPages=true",
        "-dEmbedAllFonts=true",
        # 更好的图像控制
        "-dDownsampleColorImages=true",
        "-dColorImageResolution=150",
        "-dAutoFilterColorImages=true",
        "-dColorImageFilter=/DCTEncode",
        # 灰度图像设置
        "-dDownsampleGrayImages=true", 
        "-dGrayImageResolution=150",
        "-dAutoFilterGrayImages=true",
        # 黑白图像设置
        "-dDownsampleMonoImages=true",
        "-dMonoImageResolution=300",
        f"-sOutputFile={output_path}",
        input_path
    ]
    
    try:
        result = subprocess.run(gs_command, check=True, capture_output=True, text=True)
        return True, None
    except subprocess.CalledProcessError as e:
        return False, f"GS错误: {e.stderr}"
    except FileNotFoundError:
        return False, "未找到Ghostscript，请确保已安装"

def compress_with_qpdf(input_path, output_path):
    """
    使用QPDF进行压缩
    QPDF是一个强大的PDF处理工具，对某些PDF特别有效
    """
    try:
        # 首先优化PDF结构
        subprocess.run(
            ["qpdf", "--linearize", input_path, "--replace-input"],
            check=True, capture_output=True, text=True
        )
        
        # 然后进行压缩
        subprocess.run(
            [
                "qpdf", input_path,
                "--object-streams=generate",
                "--compression-level=9",  # 最大压缩级别
                "--recompress-flate",
                "--decode-level=specialized",
                output_path
            ],
            check=True, capture_output=True, text=True
        )
        return True, None
    except subprocess.CalledProcessError as e:
        return False, f"QPDF错误: {e.stderr}"
    except FileNotFoundError:
        return False, "未找到QPDF，请确保已安装"

def compress_with_img2pdf(input_path, output_path, dpi=150):
    """
    采用img2pdf策略 - 转换为图像后重新创建PDF
    对于一些特殊PDF非常有效，但可能会降低文本可选择性
    """
    try:
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 使用pdftoppm转换为图像
            img_prefix = os.path.join(temp_dir, "page")
            
            # 转换PDF为图像
            subprocess.run(
                ["pdftoppm", "-png", "-r", str(dpi), input_path, img_prefix],
                check=True, capture_output=True, text=True
            )
            
            # 获取所有生成的PNG图像并排序
            images = sorted([
                os.path.join(temp_dir, f) for f in os.listdir(temp_dir)
                if f.endswith(".png")
            ])
            
            if not images:
                return False, "转换为图像失败，未生成任何图像"
            
            # 使用img2pdf重新创建PDF (保持高质量，但文件大小更小)
            subprocess.run(
                ["img2pdf"] + images + ["-o", output_path],
                check=True, capture_output=True, text=True
            )
            
            return True, None
    except subprocess.CalledProcessError as e:
        return False, f"转换错误: {e.stderr}"
    except FileNotFoundError as e:
        tool = "pdftoppm" if "pdftoppm" in str(e) else "img2pdf"
        return False, f"未找到{tool}，请确保已安装"

def compress_with_ocrmypdf(input_path, output_path):
    """
    使用OCRmyPDF进行光学字符识别和压缩
    适用于扫描的文档，可以显著减小文件大小并增加文本可搜索性
    """
    try:
        subprocess.run(
            [
                "ocrmypdf",
                "--optimize", "3",  # 最高优化级别
                "--skip-text",      # 跳过已有文本
                "--deskew",         # 纠正倾斜
                "--clean",          # 清理图像
                "--rotate-pages",   # 自动旋转页面
                input_path, output_path
            ],
            check=True, capture_output=True, text=True
        )
        return True, None
    except subprocess.CalledProcessError as e:
        return False, f"OCRmyPDF错误: {e.stderr}"
    except FileNotFoundError:
        return False, "未找到OCRmyPDF，请确保已安装"

def compress_pdf(input_path, output_path=None, method="advanced-gs", dpi=150, verbose=True):
    """
    压缩PDF文件，使用多种方法
    
    参数:
    - input_path: 输入PDF路径
    - output_path: 输出PDF路径 (如果为None，则覆盖原文件)
    - method: 压缩方法
      - "advanced-gs": 使用高级Ghostscript设置 (默认)
      - "qpdf": 使用QPDF
      - "img2pdf": 转换为图像后重新创建PDF
      - "ocrmypdf": 使用OCRmyPDF (适用于扫描文档)
      - "all": 尝试所有方法，选择最佳结果
    - dpi: 图像分辨率 (适用于img2pdf方法)
    - verbose: 是否显示详细信息
    
    返回:
    - 成功与否
    - 压缩率信息
    """
    if not os.path.exists(input_path):
        logger.error(f"错误: 找不到文件 {input_path}")
        return False, None
    
    # 获取原始文件大小
    original_size = os.path.getsize(input_path)
    
    # 如果没有指定输出路径，创建临时文件
    is_temp = False
    if output_path is None:
        is_temp = True
        temp_fd, output_path = tempfile.mkstemp(suffix=".pdf")
        os.close(temp_fd)
    
    # 用于存储所有压缩结果的列表 (用于"all"方法)
    results = []
    
    # 尝试指定的压缩方法
    if method == "all":
        methods = ["advanced-gs", "qpdf", "img2pdf", "ocrmypdf"]
        logger.info("尝试所有压缩方法，将选择最佳结果")
        
        for m in methods:
            temp_output = tempfile.mktemp(suffix=".pdf")
            success, error = compress_with_method(input_path, temp_output, m, dpi)
            
            if success:
                size = os.path.getsize(temp_output)
                results.append((m, temp_output, size))
                logger.info(f"方法 {m} 成功: {size/1024:.2f} KB")
            else:
                logger.warning(f"方法 {m} 失败: {error}")
        
        # 如果没有成功的方法，返回失败
        if not results:
            logger.error("所有压缩方法均失败")
            return False, None
        
        # 选择文件大小最小的结果
        best_method, best_output, best_size = min(results, key=lambda x: x[2])
        logger.info(f"最佳方法: {best_method}，大小: {best_size/1024:.2f} KB")
        
        # 移动到目标位置
        shutil.copy2(best_output, output_path)
        
        # 清理临时文件
        for _, temp_file, _ in results:
            try:
                os.remove(temp_file)
            except:
                pass
    else:
        # 使用单一方法
        success, error = compress_with_method(input_path, output_path, method, dpi)
        if not success:
            logger.error(f"压缩失败: {error}")
            if is_temp:
                os.remove(output_path)
            return False, None
    
    # 获取压缩后的文件大小
    compressed_size = os.path.getsize(output_path)
    
    # 如果压缩后文件大于原始文件，不采用压缩结果
    if compressed_size >= original_size:
        logger.warning("压缩未能减小文件大小，保持原始文件")
        if is_temp:
            os.remove(output_path)
        return False, None
    
    # 计算压缩率
    compression_ratio = (1 - compressed_size / original_size) * 100
    
    if verbose:
        logger.info(f"原始大小: {original_size / 1024:.2f} KB")
        logger.info(f"压缩后大小: {compressed_size / 1024:.2f} KB")
        logger.info(f"压缩率: {compression_ratio:.2f}%")
    
    # 如果是临时文件，替换原始文件
    if is_temp:
        shutil.move(output_path, input_path)
    
    return True, compression_ratio

def compress_with_method(input_path, output_path, method, dpi):
    """根据指定的方法压缩PDF"""
    if method == "advanced-gs":
        return compress_with_gs_high_quality(input_path, output_path)
    elif method == "qpdf":
        return compress_with_qpdf(input_path, output_path)
    elif method == "img2pdf":
        return compress_with_img2pdf(input_path, output_path, dpi)
    elif method == "ocrmypdf":
        return compress_with_ocrmypdf(input_path, output_path)
    else:
        return False, f"未知的压缩方法: {method}"

def process_directory(input_dir, output_dir, method="advanced-gs", dpi=150, verbose=True):
    """
    处理整个目录的PDF文件
    
    参数:
    - input_dir: 输入目录路径
    - output_dir: 输出目录路径
    - method: 压缩方法
    - dpi: 图像分辨率 (用于img2pdf方法)
    - verbose: 是否显示详细信息
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有PDF文件
    input_dir_path = Path(input_dir)
    pdf_files = list(input_dir_path.glob("**/*.pdf"))
    
    if not pdf_files:
        logger.warning(f"在 {input_dir} 中未找到PDF文件")
        return
    
    total_files = len(pdf_files)
    success_count = 0
    total_saved = 0
    failed_files = []
    
    if verbose:
        logger.info(f"找到 {total_files} 个PDF文件需要处理")
    
    for i, pdf_file in enumerate(pdf_files, 1):
        # 保持相对路径结构
        rel_path = pdf_file.relative_to(input_dir_path)
        output_path = Path(output_dir) / rel_path
        
        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if verbose:
            logger.info(f"\n处理 [{i}/{total_files}]: {rel_path}")
        
        success, compression_ratio = compress_pdf(
            str(pdf_file), str(output_path), method, dpi, verbose)
        
        if success:
            success_count += 1
            if compression_ratio:
                original_size = os.path.getsize(pdf_file) / 1024
                compressed_size = os.path.getsize(output_path) / 1024
                saved_kb = original_size - compressed_size
                total_saved += saved_kb
        else:
            failed_files.append(str(rel_path))
    
    if verbose:
        logger.info(f"\n压缩完成: {success_count}/{total_files} 文件成功压缩")
        logger.info(f"总共节省: {total_saved:.2f} KB")
        
        if failed_files:
            logger.warning("以下文件压缩失败:")
            for f in failed_files:
                logger.warning(f"  - {f}")

def main():
    parser = argparse.ArgumentParser(description="高级PDF文件压缩工具")
    parser.add_argument("input", help="输入PDF文件路径或目录路径")
    parser.add_argument("-o", "--output", help="输出PDF文件路径或目录路径 (默认覆盖原文件)")
    parser.add_argument(
        "-m", "--method", 
        choices=["advanced-gs", "qpdf", "img2pdf", "ocrmypdf", "all"],
        default="advanced-gs",
        help="压缩方法 (默认: advanced-gs)"
    )
    parser.add_argument(
        "--dpi", type=int, default=150,
        help="图像分辨率 (用于img2pdf方法，默认: 150)"
    )
    parser.add_argument("--silent", action="store_true", help="静默模式，不显示详细信息")
    parser.add_argument("--batch", action="store_true", help="批处理模式，处理整个目录")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.silent:
        logger.setLevel(logging.WARNING)
    
    # 批处理模式，处理整个目录
    if args.batch or os.path.isdir(args.input):
        if not args.output:
            logger.error("错误: 批处理模式下必须指定输出目录")
            return
        process_directory(args.input, args.output, args.method, args.dpi, not args.silent)
    else:
        # 单文件模式
        compress_pdf(args.input, args.output, args.method, args.dpi, not args.silent)

if __name__ == "__main__":
    main()