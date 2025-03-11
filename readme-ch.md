一个使用PyPDF2和pikepdf库来压缩PDF文件的实现：

这个Python脚本提供了一个灵活的PDF压缩解决方案，它有以下几个特点：

1. **两种压缩方法**：
   - 使用Ghostscript进行高质量压缩（主要方法）
   - 使用pikepdf作为备选方法（当Ghostscript不可用时）

2. **可调节的压缩质量**：
   - screen：屏幕质量 (72 dpi)，文件最小但质量较低
   - ebook：电子书质量 (150 dpi)，平衡文件大小和质量
   - printer：打印质量 (300 dpi)，默认选项，保持较好清晰度
   - prepress：印刷质量 (300 dpi)，保留更多色彩信息
   - default：默认质量设置

3. **智能处理**：
   - 如果压缩后文件变大，会保留原始文件
   - 提供压缩率统计
   - 支持直接替换原文件或输出到新文件

4. **命令行接口**：
   - 易于集成到批处理脚本或其他工作流程中
   - 可以调整压缩质量和输出选项

### 使用方法

1. 安装依赖：
```bash
pip install pikepdf
```

2. 确保安装了Ghostscript（可选但推荐）：
   - 在Windows上：下载并安装 Ghostscript，确保添加到系统PATH
   - 在Linux上：`sudo apt-get install ghostscript` 或对应的包管理器命令
   - 在macOS上：`brew install ghostscript`

3. 使用示例：
```bash
# 基本用法（覆盖原文件）
python main.py document.pdf

# 指定输出文件
python main.py document.pdf -o compressed.pdf

# 调整压缩质量
python main.py document.pdf -q ebook

# 静默模式
python main.py document.pdf --silent
```

要获得最佳的压缩效果同时保持文档的清晰度，建议使用"printer"或"ebook"质量设置。如果文档中包含大量高质量图像且需要保持图像质量，可以使用"prepress"设置。

### 使用方法

1. 将两个Python文件放在同一个目录下：
   - `main.py`（原始的压缩工具）
   - `b2b.py`（新创建的专用脚本）

2. 确保在同级目录下有一个名为`books`的文件夹，包含你要压缩的PDF文件

3. 运行脚本：
```bash
python b2b.py
```

4. 可以选择指定压缩质量：
```bash
python b2b.py ebook   # 使用ebook质量（较小的文件）
python b2b.py prepress   # 使用prepress质量（较高品质）
```

脚本会自动处理`books`目录下的所有PDF文件，并将压缩后的版本保存到`eBooks`目录，同时保持原始文件名不变。完成后，你会看到处理了多少文件以及总共节省了多少空间的统计信息。