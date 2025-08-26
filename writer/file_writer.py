#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件写入器
写入修改后的文件
支持备份原始文件（如 .bak）
支持输出迁移报告（统计替换数量）
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from config import Config


class FileWriter:
    """文件写入器类"""
    
    def __init__(self, config: Config):
        self.config = config
        self.backup_dir = None
        self.migration_log = []
        
        # 创建备份目录
        if self.config.BACKUP_ENABLED:
            self._create_backup_directory()
    
    def _create_backup_directory(self):
        """创建备份目录"""
        project_path = Path(self.config.PROJECT_PATH)
        backup_dir = project_path / "butterknife_backup"
        
        if not backup_dir.exists():
            backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.backup_dir = backup_dir
    
    def write_file(self, file_path: str, content: str) -> bool:
        """
        写入文件
        
        Args:
            file_path: 文件路径
            content: 文件内容
            
        Returns:
            是否成功写入
        """
        try:
            file_path_obj = Path(file_path)
            
            # 检查文件是否存在
            if not file_path_obj.exists():
                print(f"警告: 文件不存在: {file_path}")
                return False
            
            # 创建备份
            if self.config.BACKUP_ENABLED and self.backup_dir:
                self._create_backup(file_path)
            
            # 写入新内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 记录迁移日志
            self._log_migration(file_path, True, "文件写入成功")
            
            return True
            
        except Exception as e:
            error_msg = f"写入文件失败: {e}"
            print(error_msg)
            self._log_migration(file_path, False, error_msg)
            return False
    
    def _create_backup(self, file_path: str):
        """创建文件备份"""
        if not self.backup_dir:
            return
        
        try:
            file_path_obj = Path(file_path)
            project_path = Path(self.config.PROJECT_PATH)
            
            # 计算相对路径
            try:
                relative_path = file_path_obj.relative_to(project_path)
            except ValueError:
                # 如果文件不在项目目录内，使用文件名
                relative_path = file_path_obj.name
            
            # 创建备份文件路径
            backup_file_path = self.backup_dir / relative_path
            
            # 创建必要的目录
            backup_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            shutil.copy2(file_path, backup_file_path)
            
            # 记录备份信息
            self._log_migration(file_path, True, f"备份文件已创建: {backup_file_path}")
            
        except Exception as e:
            print(f"创建备份失败: {e}")
    
    def _log_migration(self, file_path: str, success: bool, message: str):
        """记录迁移日志"""
        log_entry = {
            'file_path': file_path,
            'success': success,
            'message': message,
            'timestamp': self._get_timestamp()
        }
        
        self.migration_log.append(log_entry)
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_migration_summary(self) -> Dict[str, Any]:
        """获取迁移摘要"""
        total_files = len(self.migration_log)
        successful_files = sum(1 for entry in self.migration_log if entry['success'])
        failed_files = total_files - successful_files
        
        return {
            'total_files': total_files,
            'successful_files': successful_files,
            'failed_files': failed_files,
            'success_rate': (successful_files / total_files * 100) if total_files > 0 else 0,
            'backup_enabled': self.config.BACKUP_ENABLED,
            'backup_directory': str(self.backup_dir) if self.backup_dir else None
        }
    
    def get_detailed_log(self) -> List[Dict[str, Any]]:
        """获取详细日志"""
        return self.migration_log.copy()
    
    def export_migration_report(self, output_path: str) -> bool:
        """导出迁移报告"""
        try:
            import json
            
            report = {
                'summary': self.get_migration_summary(),
                'detailed_log': self.get_detailed_log(),
                'config': {
                    'project_path': self.config.PROJECT_PATH,
                    'binding_mode': self.config.BINDING_MODE,
                    'backup_enabled': self.config.BACKUP_ENABLED,
                    'backup_extension': self.config.BACKUP_EXTENSION
                }
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"导出迁移报告失败: {e}")
            return False
    
    def print_migration_summary(self):
        """打印迁移摘要"""
        summary = self.get_migration_summary()
        
        print("\n" + "="*60)
        print("文件迁移摘要")
        print("="*60)
        print(f"总文件数: {summary['total_files']}")
        print(f"成功迁移: {summary['successful_files']}")
        print(f"迁移失败: {summary['failed_files']}")
        print(f"成功率: {summary['success_rate']:.1f}%")
        print(f"备份功能: {'启用' if summary['backup_enabled'] else '禁用'}")
        
        if summary['backup_directory']:
            print(f"备份目录: {summary['backup_directory']}")
        
        print("="*60)
    
    def print_detailed_log(self, max_entries: int = 10):
        """打印详细日志"""
        log_entries = self.get_detailed_log()
        
        if not log_entries:
            print("暂无迁移日志")
            return
        
        print(f"\n详细迁移日志 (显示最近 {min(max_entries, len(log_entries))} 条):")
        print("-" * 80)
        
        # 显示最近的日志条目
        recent_entries = log_entries[-max_entries:]
        
        for entry in recent_entries:
            status = "✓" if entry['success'] else "✗"
            file_name = Path(entry['file_path']).name
            message = entry['message']
            timestamp = entry['timestamp']
            
            print(f"{status} {file_name} - {message}")
            print(f"    时间: {timestamp}")
            print()
    
    def cleanup_backup(self) -> bool:
        """清理备份文件"""
        if not self.backup_dir or not self.backup_dir.exists():
            return True
        
        try:
            shutil.rmtree(self.backup_dir)
            self.backup_dir = None
            print(f"备份目录已清理: {self.backup_dir}")
            return True
            
        except Exception as e:
            print(f"清理备份目录失败: {e}")
            return False
    
    def restore_from_backup(self, file_path: str) -> bool:
        """从备份恢复文件"""
        if not self.backup_dir or not self.backup_dir.exists():
            print("备份目录不存在")
            return False
        
        try:
            file_path_obj = Path(file_path)
            project_path = Path(self.config.PROJECT_PATH)
            
            # 计算相对路径
            try:
                relative_path = file_path_obj.relative_to(project_path)
            except ValueError:
                relative_path = file_path_obj.name
            
            # 查找备份文件
            backup_file_path = self.backup_dir / relative_path
            
            if not backup_file_path.exists():
                print(f"备份文件不存在: {backup_file_path}")
                return False
            
            # 恢复文件
            shutil.copy2(backup_file_path, file_path)
            print(f"文件已从备份恢复: {file_path}")
            
            return True
            
        except Exception as e:
            print(f"从备份恢复文件失败: {e}")
            return False
    
    def get_backup_info(self) -> Dict[str, Any]:
        """获取备份信息"""
        if not self.backup_dir or not self.backup_dir.exists():
            return {
                'backup_enabled': False,
                'backup_directory': None,
                'backup_file_count': 0,
                'backup_size': 0
            }
        
        try:
            backup_files = list(self.backup_dir.rglob('*'))
            backup_file_count = len([f for f in backup_files if f.is_file()])
            
            # 计算备份目录大小
            backup_size = sum(f.stat().st_size for f in backup_files if f.is_file())
            
            return {
                'backup_enabled': True,
                'backup_directory': str(self.backup_dir),
                'backup_file_count': backup_file_count,
                'backup_size': backup_size,
                'backup_size_mb': backup_size / (1024 * 1024)
            }
            
        except Exception as e:
            print(f"获取备份信息失败: {e}")
            return {
                'backup_enabled': False,
                'backup_directory': None,
                'backup_file_count': 0,
                'backup_size': 0
            }
