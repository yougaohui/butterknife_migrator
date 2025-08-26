#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件扫描器模块
遍历项目目录，返回所有 .java 文件路径
支持过滤 Activity、Fragment、Adapter 等类型
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Set
from config import Config


class FileScanner:
    """文件扫描器类"""
    
    def __init__(self, config: Config):
        self.config = config
        self.java_files_cache = []
        self.file_types_cache = {}
        
    def scan_files(self) -> List[str]:
        """扫描项目中的所有Java文件"""
        if self.java_files_cache:
            return self.java_files_cache
        
        java_files = []
        scan_paths = self.config.get_scan_paths()
        
        for scan_path in scan_paths:
            if os.path.exists(scan_path):
                java_files.extend(self._scan_directory(scan_path))
        
        # 去重并排序
        java_files = sorted(list(set(java_files)))
        self.java_files_cache = java_files
        
        return java_files
    
    def _scan_directory(self, directory: str) -> List[str]:
        """扫描指定目录下的Java文件"""
        java_files = []
        
        try:
            for root, dirs, files in os.walk(directory):
                # 排除不需要的目录
                dirs[:] = [d for d in dirs if not self._should_exclude_directory(d)]
                
                for file in files:
                    if self._should_include_file(file):
                        file_path = os.path.join(root, file)
                        java_files.append(file_path)
                        
        except Exception as e:
            print(f"扫描目录 {directory} 时出错: {e}")
        
        return java_files
    
    def _should_exclude_directory(self, dir_name: str) -> bool:
        """判断是否应该排除目录"""
        exclude_dirs = self.config.EXCLUDE_DIRECTORIES
        
        for exclude_dir in exclude_dirs:
            if exclude_dir in dir_name:
                return True
        
        return False
    
    def _should_include_file(self, file_name: str) -> bool:
        """判断是否应该包含文件"""
        # 检查文件扩展名
        if not any(file_name.endswith(ext) for ext in self.config.SCAN_EXTENSIONS):
            return False
        
        # 检查排除的文件模式
        for exclude_pattern in self.config.EXCLUDE_PATTERNS:
            if exclude_pattern in file_name:
                return False
        
        return True
    
    def get_file_types(self) -> Dict[str, Set[str]]:
        """获取文件类型分类"""
        if self.file_types_cache:
            return self.file_types_cache
        
        java_files = self.scan_files()
        file_types = {
            'activities': set(),
            'fragments': set(),
            'adapters': set(),
            'views': set(),
            'others': set()
        }
        
        for file_path in java_files:
            file_type = self._classify_file(file_path)
            file_types[file_type].add(file_path)
        
        self.file_types_cache = file_types
        return file_types
    
    def _classify_file(self, file_path: str) -> str:
        """分类文件类型"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否是Activity
            if self._is_activity(content):
                return 'activities'
            
            # 检查是否是Fragment
            if self._is_fragment(content):
                return 'fragments'
            
            # 检查是否是Adapter
            if self._is_adapter(content):
                return 'adapters'
            
            # 检查是否是View
            if self._is_view(content):
                return 'views'
            
            return 'others'
            
        except Exception:
            return 'others'
    
    def _is_activity(self, content: str) -> bool:
        """判断是否是Activity类"""
        patterns = [
            r'class\s+\w+\s+extends\s+\w*Activity',
            r'class\s+\w+\s+implements\s+.*Activity',
            r'@Override\s+protected\s+void\s+onCreate\s*\(',
            r'extends\s+AppCompatActivity',
            r'extends\s+FragmentActivity'
        ]
        
        return any(re.search(pattern, content, re.MULTILINE) for pattern in patterns)
    
    def _is_fragment(self, content: str) -> bool:
        """判断是否是Fragment类"""
        patterns = [
            r'class\s+\w+\s+extends\s+\w*Fragment',
            r'@Override\s+public\s+View\s+onCreateView\s*\(',
            r'@Override\s+public\s+void\s+onViewCreated\s*\('
        ]
        
        return any(re.search(pattern, content, re.MULTILINE) for pattern in patterns)
    
    def _is_adapter(self, content: str) -> bool:
        """判断是否是Adapter类"""
        patterns = [
            r'class\s+\w+\s+extends\s+\w*Adapter',
            r'implements\s+.*Adapter',
            r'getView\s*\(',
            r'onBindViewHolder\s*\('
        ]
        
        return any(re.search(pattern, content, re.MULTILINE) for pattern in patterns)
    
    def _is_view(self, content: str) -> bool:
        """判断是否是View类"""
        patterns = [
            r'class\s+\w+\s+extends\s+\w*View',
            r'class\s+\w+\s+extends\s+\w*ViewGroup',
            r'onDraw\s*\(',
            r'onMeasure\s*\('
        ]
        
        return any(re.search(pattern, content, re.MULTILINE) for pattern in patterns)
    
    def get_files_by_type(self, file_type: str) -> List[str]:
        """根据类型获取文件列表"""
        file_types = self.get_file_types()
        return list(file_types.get(file_type, set()))
    
    def get_statistics(self) -> Dict[str, int]:
        """获取文件统计信息"""
        file_types = self.get_file_types()
        stats = {}
        
        for file_type, files in file_types.items():
            stats[file_type] = len(files)
        
        stats['total'] = len(self.scan_files())
        return stats
    
    def clear_cache(self):
        """清除缓存"""
        self.java_files_cache.clear()
        self.file_types_cache.clear()
    
    def refresh(self):
        """刷新扫描结果"""
        self.clear_cache()
        return self.scan_files()


class FileScannerFactory:
    """文件扫描器工厂类"""
    
    @staticmethod
    def create_scanner(config: Config) -> FileScanner:
        """创建文件扫描器实例"""
        return FileScanner(config)
    
    @staticmethod
    def create_scanner_with_options(
        project_path: str,
        scan_extensions: List[str] = None,
        exclude_dirs: List[str] = None
    ) -> FileScanner:
        """使用自定义选项创建文件扫描器"""
        config = Config()
        config.PROJECT_PATH = project_path
        
        if scan_extensions:
            config.SCAN_EXTENSIONS = scan_extensions
        
        if exclude_dirs:
            config.EXCLUDE_DIRECTORIES = exclude_dirs
        
        return FileScanner(config)
