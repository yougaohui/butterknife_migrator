#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ButterKnife自动迁移工具
自动检测当前目录并执行迁移
"""

import os
import sys
import json
from pathlib import Path

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from config import Config
from scanner.file_scanner import FileScanner
from butterknife_parser_module.butterknife_parser import ButterKnifeParser
from transformer.findview_transformer import FindViewTransformer
from transformer.onclick_transformer import OnClickTransformer
from transformer.bindcall_remover import BindCallRemover
from injector.code_injector import CodeInjector
from writer.file_writer import FileWriter
from utils.logger import Logger
from utils.code_formatter import CodeFormatter


class AutoButterKnifeMigrator:
    """自动ButterKnife迁移工具"""
    
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.scanner = FileScanner(self.config)
        self.parser = ButterKnifeParser()
        self.formatter = CodeFormatter()
        self.transformers = [
            FindViewTransformer(),
            OnClickTransformer(),
            BindCallRemover()
        ]
        self.injector = CodeInjector()
        self.writer = FileWriter(self.config)
        
    def detect_project_type(self):
        """检测项目类型"""
        current_dir = os.getcwd()
        
        # 检查是否是Android项目
        android_indicators = [
            "app/build.gradle",
            "build.gradle",
            "settings.gradle",
            "gradle.properties"
        ]
        
        is_android = any(os.path.exists(os.path.join(current_dir, indicator)) for indicator in android_indicators)
        
        if is_android:
            self.logger.info(f"检测到Android项目: {current_dir}")
            return "android"
        else:
            self.logger.info(f"检测到普通Java项目: {current_dir}")
            return "java"
    
    def auto_scan_directories(self):
        """自动扫描目录"""
        current_dir = os.getcwd()
        scan_dirs = []
        
        # 常见的Java源码目录
        common_dirs = [
            "app/src/main/java",
            "src/main/java", 
            "src/java",
            "java",
            "src",
            "app/src",
            "tests",
            "test"
        ]
        
        for dir_name in common_dirs:
            full_path = os.path.join(current_dir, dir_name)
            if os.path.exists(full_path) and os.path.isdir(full_path):
                scan_dirs.append(dir_name)
                self.logger.info(f"发现源码目录: {dir_name}")
        
        if not scan_dirs:
            # 如果没有找到标准目录，扫描当前目录下的所有子目录
            for item in os.listdir(current_dir):
                item_path = os.path.join(current_dir, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    scan_dirs.append(item)
                    self.logger.info(f"发现目录: {item}")
        
        return scan_dirs
    
    def migrate(self):
        """执行自动迁移"""
        try:
            print("=" * 60)
            print("🚀 ButterKnife 自动迁移工具")
            print("=" * 60)
            
            # 检测项目类型
            project_type = self.detect_project_type()
            
            # 自动扫描目录
            auto_dirs = self.auto_scan_directories()
            if auto_dirs:
                self.config.SCAN_DIRECTORIES = auto_dirs
                self.logger.info(f"自动配置扫描目录: {auto_dirs}")
            
            print(f"📁 项目路径: {self.config.PROJECT_PATH}")
            print(f"📂 扫描目录: {', '.join(self.config.SCAN_DIRECTORIES)}")
            print(f"🔍 扫描文件类型: {', '.join(self.config.SCAN_EXTENSIONS)}")
            print()
            
            # 1. 扫描文件
            print("🔍 正在扫描Java文件...")
            java_files = self.scanner.scan_files()
            
            if not java_files:
                print("❌ 未找到任何Java文件")
                return False
            
            print(f"✅ 找到 {len(java_files)} 个Java文件")
            
            # 2. 解析和迁移
            migrated_count = 0
            total_butterknife_files = 0
            
            for file_path in java_files:
                try:
                    print(f"📄 处理文件: {file_path}")
                    
                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 检测格式化问题
                    issues = self.formatter.detect_formatting_issues(content)
                    if issues:
                        print(f"   🔧 发现格式化问题: {', '.join(issues)}")
                        # 格式化代码
                        content = self.formatter.format_entire_file(content)
                        print(f"   ✅ 代码格式化完成")
                    
                    # 解析ButterKnife注解
                    parsed_data = self.parser.parse(content)
                    
                    if not parsed_data.get('has_butterknife', False):
                        print(f"   ⏭️  跳过（无ButterKnife注解）")
                        continue
                    
                    total_butterknife_files += 1
                    print(f"   🔧 发现ButterKnife注解，开始迁移...")
                    
                    # 应用转换器
                    transformed_content = content
                    for transformer in self.transformers:
                        transformed_content = transformer.transform(parsed_data, transformed_content)
                    
                    # 注入代码
                    final_content = self.injector.inject(transformed_content, parsed_data)
                    
                    # 写入文件
                    self.writer.write_file(file_path, final_content)
                    
                    migrated_count += 1
                    print(f"   ✅ 迁移完成")
                    
                except Exception as e:
                    print(f"   ❌ 迁移失败: {str(e)}")
                    self.logger.error(f"迁移文件 {file_path} 失败: {str(e)}")
            
            # 3. 生成报告
            self.generate_report(migrated_count, total_butterknife_files, java_files)
            
            print()
            print("=" * 60)
            print("🎉 迁移完成！")
            print(f"📊 总文件数: {len(java_files)}")
            print(f"🔧 ButterKnife文件数: {total_butterknife_files}")
            print(f"✅ 成功迁移: {migrated_count}")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"❌ 迁移过程中发生错误: {str(e)}")
            self.logger.error(f"迁移过程失败: {str(e)}")
            return False
    
    def generate_report(self, migrated_count, total_butterknife_files, all_files):
        """生成迁移报告"""
        report = {
            "migration_time": str(Path().cwd()),
            "total_files": len(all_files),
            "butterknife_files": total_butterknife_files,
            "migrated_files": migrated_count,
            "success_rate": f"{(migrated_count / total_butterknife_files * 100):.1f}%" if total_butterknife_files > 0 else "0%",
            "project_path": self.config.PROJECT_PATH,
            "scan_directories": self.config.SCAN_DIRECTORIES
        }
        
        report_file = "butterknife_migration_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 迁移报告已保存到: {report_file}")


def main():
    """主函数"""
    migrator = AutoButterKnifeMigrator()
    success = migrator.migrate()
    
    if success:
        print("\n💡 提示:")
        print("- 请检查迁移后的代码")
        print("- 如有问题，可使用备份文件恢复")
        print("- 建议在版本控制系统中提交更改")
    else:
        print("\n❌ 迁移失败，请检查日志文件")
    
    input("\n按回车键退出...")


if __name__ == "__main__":
    main()
