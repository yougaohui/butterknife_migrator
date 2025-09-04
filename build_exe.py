#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建单个exe可执行文件
"""

import os
import sys
import subprocess
import shutil

def build_single_exe():
    """构建单个exe文件"""
    print("🔨 开始构建单个exe文件...")
    
    # 清理之前的构建文件
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("*.spec"):
        for spec_file in os.listdir("."):
            if spec_file.endswith(".spec"):
                os.remove(spec_file)
    
    # PyInstaller 命令
    cmd = [
        "python", "-m", "PyInstaller",
        "--onefile",                    # 打包成单个文件
        "--console",                    # 显示控制台窗口
        "--name=ButterKnifeMigrator",   # 可执行文件名称
        "--clean",                      # 清理临时文件
        "auto_migrate.py"               # 主程序文件
    ]
    
    try:
        print("执行命令:", " ".join(cmd))
        subprocess.check_call(cmd)
        print("✅ exe文件构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔨 ButterKnife 迁移工具 - 构建exe文件")
    print("=" * 60)
    
    if build_single_exe():
        exe_path = os.path.join("dist", "ButterKnifeMigrator.exe")
        if os.path.exists(exe_path):
            print(f"✅ 可执行文件已生成: {exe_path}")
            print(f"📁 文件大小: {os.path.getsize(exe_path) / 1024 / 1024:.1f} MB")
            print()
            print("📖 使用方法:")
            print("1. 将 ButterKnifeMigrator.exe 复制到你的Android项目根目录")
            print("2. 双击运行即可自动扫描和迁移")
            print("3. 查看生成的迁移报告")
        else:
            print("❌ 未找到生成的exe文件")
    else:
        print("❌ 构建失败")

if __name__ == "__main__":
    main()
