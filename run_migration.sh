#!/bin/bash

echo ""
echo "========================================"
echo "   ButterKnife 自动迁移工具"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ 错误: 未找到Python，请先安装Python 3.7+"
        echo "Ubuntu/Debian: sudo apt install python3"
        echo "CentOS/RHEL: sudo yum install python3"
        echo "macOS: brew install python3"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# 检查Python版本
echo "🔍 检查Python环境..."
$PYTHON_CMD --version

# 运行迁移工具
echo ""
echo "🚀 启动迁移工具..."
echo ""
$PYTHON_CMD auto_migrate.py

echo ""
echo "迁移完成！"
