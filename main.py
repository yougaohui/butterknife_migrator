#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ButterKnife迁移工具主控制文件
控制整个流程：扫描 → 解析 → 转换 → 注入 → 写入
"""

import argparse
import json
import os
import sys
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


class ButterKnifeMigrator:
    """ButterKnife迁移工具主类"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = Logger()
        self.scanner = FileScanner(config)
        self.parser = ButterKnifeParser()
        self.transformers = [
            FindViewTransformer(),
            OnClickTransformer(),
            BindCallRemover()
        ]
        self.injector = CodeInjector()
        self.writer = FileWriter(config)
        
    def migrate(self):
        """执行完整的迁移流程"""
        try:
            self.logger.info("开始ButterKnife迁移流程...")
            
            # 1. 扫描文件
            self.logger.info("步骤1: 扫描项目文件...")
            java_files = self.scanner.scan_files()
            self.logger.info(f"找到 {len(java_files)} 个Java文件")
            
            if not java_files:
                self.logger.warning("未找到任何Java文件，请检查项目路径配置")
                return
            
            # 2. 解析ButterKnife注解
            self.logger.info("步骤2: 解析ButterKnife注解...")
            parsed_files = []
            for file_path in java_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    parsed_data = self.parser.parse(content)
                    if parsed_data['has_butterknife']:
                        parsed_files.append({
                            'path': file_path,
                            'content': content,
                            'parsed_data': parsed_data
                        })
                        self.logger.info(f"解析文件: {Path(file_path).name}")
                except Exception as e:
                    self.logger.error(f"解析文件 {file_path} 时出错: {e}")
            
            self.logger.info(f"找到 {len(parsed_files)} 个包含ButterKnife的文件")
            
            if not parsed_files:
                self.logger.info("未找到包含ButterKnife注解的文件，无需迁移")
                return
            
            # 3. 转换代码
            self.logger.info("步骤3: 转换代码...")
            transformed_files = []
            for file_info in parsed_files:
                try:
                    transformed_content = file_info['content']
                    for transformer in self.transformers:
                        transformed_content = transformer.transform(
                            file_info['parsed_data'], 
                            transformed_content
                        )
                    
                    transformed_files.append({
                        'path': file_info['path'],
                        'original_content': file_info['content'],
                        'transformed_content': transformed_content,
                        'parsed_data': file_info['parsed_data']
                    })
                except Exception as e:
                    self.logger.error(f"转换文件 {file_info['path']} 时出错: {e}")
            
            # 4. 注入代码
            self.logger.info("步骤4: 注入初始化代码...")
            for file_info in transformed_files:
                try:
                    final_content = self.injector.inject(
                        file_info['transformed_content'],
                        file_info['parsed_data']
                    )
                    file_info['final_content'] = final_content
                except Exception as e:
                    self.logger.error(f"注入代码到文件 {file_info['path']} 时出错: {e}")
                    file_info['final_content'] = file_info['transformed_content']
            
            # 5. 写入文件
            self.logger.info("步骤5: 写入转换后的文件...")
            migration_report = {
                'total_files': len(transformed_files),
                'successful_migrations': 0,
                'failed_migrations': 0,
                'details': []
            }
            
            for file_info in transformed_files:
                try:
                    success = self.writer.write_file(
                        file_info['path'],
                        file_info['final_content']
                    )
                    
                    if success:
                        migration_report['successful_migrations'] += 1
                        self.logger.info(f"成功迁移文件: {Path(file_info['path']).name}")
                    else:
                        migration_report['failed_migrations'] += 1
                        self.logger.error(f"迁移文件失败: {Path(file_info['path']).name}")
                    
                    # 记录迁移详情
                    migration_report['details'].append({
                        'file': Path(file_info['path']).name,
                        'status': 'success' if success else 'failed',
                        'bind_views_count': len(file_info['parsed_data'].get('bind_views', [])),
                        'on_clicks_count': len(file_info['parsed_data'].get('on_clicks', [])),
                        'has_bind_call': file_info['parsed_data'].get('bind_call', False)
                    })
                    
                except Exception as e:
                    migration_report['failed_migrations'] += 1
                    self.logger.error(f"写入文件 {file_info['path']} 时出错: {e}")
            
            # 6. 生成迁移报告
            self.logger.info("步骤6: 生成迁移报告...")
            self._generate_migration_report(migration_report)
            
            self.logger.info("ButterKnife迁移流程完成!")
            
        except Exception as e:
            self.logger.error(f"迁移过程中发生错误: {e}")
            raise
    
    def _generate_migration_report(self, report: dict):
        """生成迁移报告"""
        report_path = os.path.join(self.config.PROJECT_PATH, 'butterknife_migration_report.json')
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"迁移报告已保存到: {report_path}")
            
            # 控制台输出摘要
            print("\n" + "="*50)
            print("ButterKnife迁移报告")
            print("="*50)
            print(f"总文件数: {report['total_files']}")
            print(f"成功迁移: {report['successful_migrations']}")
            print(f"迁移失败: {report['failed_migrations']}")
            print(f"成功率: {report['successful_migrations']/report['total_files']*100:.1f}%")
            print("="*50)
            
        except Exception as e:
            self.logger.error(f"生成迁移报告时出错: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='ButterKnife迁移工具')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--project-path', '-p', help='Android项目路径')
    parser.add_argument('--binding-mode', '-b', choices=['findViewById', 'viewBinding'], 
                       help='绑定模式')
    parser.add_argument('--backup', action='store_true', help='启用备份')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    try:
        # 加载配置
        if args.config:
            config = Config.from_file(args.config)
        else:
            config = Config()
        
        # 命令行参数覆盖配置文件
        if args.project_path:
            config.PROJECT_PATH = args.project_path
        if args.binding_mode:
            config.BINDING_MODE = args.binding_mode
        if args.backup is not None:
            config.BACKUP_ENABLED = args.backup
        
        # 验证配置
        if not os.path.exists(config.PROJECT_PATH):
            print(f"错误: 项目路径不存在: {config.PROJECT_PATH}")
            sys.exit(1)
        
        # 设置日志级别
        if args.verbose:
            config.LOG_LEVEL = 'DEBUG'
        
        # 执行迁移
        migrator = ButterKnifeMigrator(config)
        migrator.migrate()
        
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
