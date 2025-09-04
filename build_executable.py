#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建可执行文件脚本
使用 PyInstaller 将 ButterKnife 迁移工具打包成可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """检查 PyInstaller 是否安装"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller 已安装: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("❌ PyInstaller 未安装")
        return False

def install_pyinstaller():
    """安装 PyInstaller"""
    print("📦 正在安装 PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller 安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ PyInstaller 安装失败")
        return False

def build_executable():
    """构建可执行文件"""
    print("🔨 开始构建可执行文件...")
    
    # PyInstaller 命令参数
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包成单个文件
        "--windowed",                   # Windows 下不显示控制台窗口
        "--name=ButterKnifeMigrator",   # 可执行文件名称
        "--icon=icon.ico",              # 图标文件（如果存在）
        "--add-data=config.py;.",       # 包含配置文件
        "--add-data=scanner;scanner",   # 包含扫描模块
        "--add-data=butterknife_parser_module;butterknife_parser_module",  # 包含解析模块
        "--add-data=transformer;transformer",  # 包含转换模块
        "--add-data=injector;injector", # 包含注入模块
        "--add-data=writer;writer",     # 包含写入模块
        "--add-data=utils;utils",       # 包含工具模块
        "auto_migrate.py"               # 主程序文件
    ]
    
    # 如果没有图标文件，移除图标参数
    if not os.path.exists("icon.ico"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
    
    try:
        subprocess.check_call(cmd)
        print("✅ 可执行文件构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False

def create_distribution():
    """创建发布包"""
    print("📦 创建发布包...")
    
    dist_dir = "ButterKnifeMigrator_Distribution"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    os.makedirs(dist_dir)
    
    # 复制可执行文件
    exe_name = "ButterKnifeMigrator.exe" if os.name == 'nt' else "ButterKnifeMigrator"
    exe_path = os.path.join("dist", exe_name)
    
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, dist_dir)
        print(f"✅ 复制可执行文件: {exe_name}")
    else:
        print(f"❌ 未找到可执行文件: {exe_path}")
        return False
    
    # 复制说明文档
    files_to_copy = [
        "使用说明.md",
        "requirements.txt"
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, dist_dir)
            print(f"✅ 复制文件: {file_name}")
    
    # 创建启动脚本
    if os.name == 'nt':
        # Windows 批处理文件
        bat_content = f"""@echo off
chcp 65001 >nul
title ButterKnife 自动迁移工具

echo.
echo ========================================
echo    ButterKnife 自动迁移工具
echo ========================================
echo.

echo 🚀 启动迁移工具...
echo.

{exe_name}

echo.
echo 迁移完成！
pause
"""
        with open(os.path.join(dist_dir, "运行迁移.bat"), 'w', encoding='utf-8') as f:
            f.write(bat_content)
        print("✅ 创建 Windows 启动脚本")
    else:
        # Linux/Mac Shell 脚本
        sh_content = f"""#!/bin/bash

echo ""
echo "========================================"
echo "   ButterKnife 自动迁移工具"
echo "========================================"
echo ""

echo "🚀 启动迁移工具..."
echo ""
./{exe_name}

echo ""
echo "迁移完成！"
"""
        with open(os.path.join(dist_dir, "运行迁移.sh"), 'w', encoding='utf-8') as f:
            f.write(sh_content)
        os.chmod(os.path.join(dist_dir, "运行迁移.sh"), 0o755)
        print("✅ 创建 Linux/Mac 启动脚本")
    
    print(f"✅ 发布包创建完成: {dist_dir}")
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("🔨 ButterKnife 迁移工具 - 可执行文件构建器")
    print("=" * 60)
    
    # 检查 PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("❌ 无法安装 PyInstaller，构建终止")
            return False
    
    # 构建可执行文件
    if not build_executable():
        print("❌ 构建失败")
        return False
    
    # 创建发布包
    if not create_distribution():
        print("❌ 发布包创建失败")
        return False
    
    print()
    print("=" * 60)
    print("🎉 构建完成！")
    print("📁 发布包位置: ButterKnifeMigrator_Distribution/")
    print("📖 使用说明: 使用说明.md")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
