@echo off
chcp 65001 >nul
title ButterKnife 自动迁移工具

echo.
echo ========================================
echo    ButterKnife 自动迁移工具
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo 🔍 检查依赖...
python -c "import sys; print(f'Python版本: {sys.version}')" 2>nul
if errorlevel 1 (
    echo ❌ Python环境异常
    pause
    exit /b 1
)

REM 运行迁移工具
echo 🚀 启动迁移工具...
echo.
python auto_migrate.py

echo.
echo 迁移完成！
pause
