#!/bin/bash
#
# 环境检测脚本
# 检查 Python 和 Pillow 是否已安装
#

echo "=========================================="
echo "图片处理工具 - 环境检测"
echo "=========================================="
echo ""

# 检查 Python
echo "[1/2] 检查 Python 环境..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "  ✓ Python 已安装: $PYTHON_VERSION"
else
    echo "  ✗ Python 未安装"
    echo ""
    echo "  请安装 Python 3:"
    echo "    macOS: brew install python3"
    echo "    Ubuntu: sudo apt install python3"
    echo "    Windows: https://www.python.org/downloads/"
    exit 1
fi

# 检查 Pillow
echo ""
echo "[2/2] 检查 Pillow 库..."
if python3 -c "import PIL" 2> /dev/null; then
    PIL_VERSION=$(python3 -c "import PIL; print(PIL.__version__)")
    echo "  ✓ Pillow 已安装 (版本: $PIL_VERSION)"
else
    echo "  ✗ Pillow 未安装"
    echo ""
    echo "  请安装 Pillow:"
    echo "    pip3 install Pillow"
    echo ""
    echo "  或使用虚拟环境:"
    echo "    python3 -m venv venv"
    echo "    source venv/bin/activate  # macOS/Linux"
    echo "    venv\\Scripts\\activate     # Windows"
    echo "    pip3 install Pillow"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ 环境检查通过，可以正常使用图片处理工具"
echo "=========================================="
echo ""
echo "使用方式:"
echo "  python3 scripts/image_processor.py <文件或目录> [选项]"
echo ""
echo "查看帮助:"
echo "  python3 scripts/image_processor.py --help"
