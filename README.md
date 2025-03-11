# express-pdf
# PDF压缩工具

这是一个功能强大的PDF文件压缩工具，可以帮助您在保持文档质量的同时显著减小PDF文件大小。本工具提供多种专业级压缩策略，适用于不同类型的PDF文件。

## 功能特点

- **多种压缩方法**：支持4种专业级压缩算法
- **批量处理**：可以处理整个目录的PDF文件
- **智能压缩**：自动选择最佳压缩效果
- **质量控制**：平衡文件大小和文档质量
- **命令行接口**：易于集成到自动化流程中

## 压缩方法

本工具提供以下压缩方法：

1. **高级Ghostscript (`advanced-gs`)**：
   - 精细调整的Ghostscript参数配置
   - 适合大多数普通PDF文档
   - 平衡压缩率和文档质量

2. **QPDF (`qpdf`)**：
   - 专业的PDF优化工具
   - 对带有大量矢量图形的PDF特别有效
   - 保持文档结构完整性

3. **图像转换 (`img2pdf`)**：
   - 将PDF转换为图像后重新构建
   - 压缩率非常高
   - 适合复杂排版的文档（如杂志、广告）
   - 注意：可能会影响文本选择和搜索

4. **OCR压缩 (`ocrmypdf`)**：
   - 专为扫描文档设计
   - 同时进行OCR识别和压缩
   - 使文本可搜索，同时减小文件大小

5. **全方法尝试 (`all`)**：
   - 尝试所有可用方法，选择最佳结果
   - 最推荐的压缩方式（但速度较慢）

## 安装依赖

根据您计划使用的压缩方法，需要安装不同的依赖：

### 基本依赖

```bash
pip install pikepdf
```

### 高级Ghostscript方法

- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt-get install ghostscript
  ```
- **Windows**:
  下载并安装 [Ghostscript](https://www.ghostscript.com/download/gsdnld.html)
- **macOS**:
  ```bash
  brew install ghostscript
  ```

### QPDF方法

- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt-get install qpdf
  ```
- **Windows**:
  下载并安装 [QPDF](https://github.com/qpdf/qpdf/releases)
- **macOS**:
  ```bash
  brew install qpdf
  ```

### img2pdf方法

```bash
pip install img2pdf
```

同时需要安装poppler-utils：
- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt-get install poppler-utils
  ```
- **Windows**:
  下载并安装 [poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases)
- **macOS**:
  ```bash
  brew install poppler
  ```

### OCRmyPDF方法

```bash
pip install ocrmypdf
```

同时需要安装Tesseract OCR引擎：
- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt-get install tesseract-ocr
  # 对于中文文档，还需要安装中文语言包
  sudo apt-get install tesseract-ocr-chi-sim
  ```
- **Windows**:
  下载并安装 [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**:
  ```bash
  brew install tesseract
  ```

## 使用方法

### 基本用法

1. 压缩单个PDF文件：

```bash
python advanced_pdf_compressor.py input.pdf -o output.pdf
```

2. 使用指定的压缩方法：

```bash
python advanced_pdf_compressor.py input.pdf -o output.pdf -m qpdf
```

3. 批量处理整个目录：

```bash
python advanced_pdf_compressor.py input_directory -o output_directory --batch
```

### books目录到eBooks目录的快捷脚本

我们提供了一个专门的脚本，用于将`books`目录中的PDF文件压缩后输出到`eBooks`目录：

1. 使用默认方法（高级Ghostscript）：

```bash
python books_to_ebooks_advanced.py
```

2. 尝试所有方法并选择最佳结果（推荐但较慢）：

```bash
python books_to_ebooks_advanced.py all
```

3. 使用特定方法并设置DPI（用于img2pdf方法）：

```bash
python books_to_ebooks_advanced.py img2pdf 200
```

## 命令行参数

### advanced_pdf_compressor.py

```
usage: advanced_pdf_compressor.py [-h] [-o OUTPUT] [-m {advanced-gs,qpdf,img2pdf,ocrmypdf,all}] 
                                 [--dpi DPI] [--silent] [--batch] input

参数说明:
  input                   输入PDF文件路径或目录路径
  -o, --output            输出PDF文件路径或目录路径
  -m, --method            压缩方法 (默认: advanced-gs)
  --dpi DPI               图像分辨率 (用于img2pdf方法，默认: 150)
  --silent                静默模式，不显示详细信息
  --batch                 批处理模式，处理整个目录
  -h, --help              显示帮助信息
```

### books_to_ebooks_advanced.py

```
usage: books_to_ebooks_advanced.py [method] [dpi]

参数说明:
  method                  压缩方法 (可选: advanced-gs, qpdf, img2pdf, ocrmypdf, all)
                         不指定则使用默认方法: advanced-gs
  dpi                     图像分辨率 (仅用于img2pdf方法，默认: 150)
```

## 示例场景

1. **电子书收藏压缩**:
   ```bash
   python books_to_ebooks_advanced.py ebook
   ```

2. **扫描文档处理**:
   ```bash
   python books_to_ebooks_advanced.py ocrmypdf
   ```

3. **杂志/图片密集型PDF**:
   ```bash
   python books_to_ebooks_advanced.py img2pdf 200
   ```

4. **重要文档最佳压缩**:
   ```bash
   python books_to_ebooks_advanced.py all
   ```

## 选择合适的压缩方法

- **文本为主的普通PDF**: 使用`advanced-gs`或`qpdf`
- **带有复杂矢量图形的PDF**: 使用`qpdf`
- **图像密集型PDF/杂志/彩色文档**: 使用`img2pdf`
- **扫描文档/图像PDF**: 使用`ocrmypdf`
- **如果不确定或追求最佳压缩**: 使用`all`

## 注意事项

1. 压缩PDF可能会影响文档质量，特别是使用`img2pdf`方法时
2. 始终保留原始文件的备份
3. 对于重要文档，请在使用前验证压缩后的文件质量
4. `all`方法会尝试所有可用的压缩方法，这可能需要较长时间
5. 文件大小减小程度取决于原始PDF的特性和选择的压缩方法

## 故障排除

**问题**: 压缩后文件大小未减小  
**解决方案**: 尝试不同的压缩方法，或者检查原始PDF是否已经压缩

**问题**: 压缩过程报错  
**解决方案**: 确保已安装相应的依赖，查看详细错误信息

**问题**: 使用`ocrmypdf`方法出错  
**解决方案**: 确保已安装Tesseract和相应的语言包

**问题**: 图像质量明显下降  
**解决方案**: 对于`img2pdf`方法，尝试增加DPI值（如200或300）

## 项目文件

- `main.py`: 主要压缩工具
- `b2b.py`: books到eBooks目录的便捷脚本

## 许可证

MIT