#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ButterKnife迁移工具配置文件
"""

import json
import os
from pathlib import Path


class Config:
    """配置类"""
    
    def __init__(self):
        # 项目路径
        self.PROJECT_PATH = os.getcwd()
        
        # 绑定模式: findViewById 或 viewBinding
        self.BINDING_MODE = "findViewById"
        
        # 是否启用备份
        self.BACKUP_ENABLED = True
        
        # 备份文件扩展名
        self.BACKUP_EXTENSION = ".bak"
        
        # 日志级别
        self.LOG_LEVEL = "INFO"
        
        # 日志文件路径
        self.LOG_FILE = "butterknife_migration.log"
        
        # 扫描的文件类型
        self.SCAN_EXTENSIONS = [".java"]
        
        # 扫描的目录（相对于项目根目录）
        self.SCAN_DIRECTORIES = [
            "app/src/main/java",
            "src/main/java",
            "java",
            "tests"  # 添加tests目录用于测试
        ]
        
        # 排除的目录
        self.EXCLUDE_DIRECTORIES = [
            "build",
            ".gradle",
            ".idea",
            "bin",
            "gen"
            # 移除 "butterknife_backup" 以允许扫描tests目录下的文件
        ]
        
        # 排除的文件模式
        self.EXCLUDE_PATTERNS = [
            "R.java",
            "BuildConfig.java"
        ]
        
        # ViewBinding相关配置
        self.VIEWBINDING_PACKAGE = "androidx.databinding"
        self.VIEWBINDING_IMPORT = "androidx.databinding.ViewBinding"
        
        # 代码风格配置
        self.INDENT_SIZE = 4
        self.USE_SPACES = True
        
        # 迁移选项
        self.REMOVE_BUTTERKNIFE_IMPORTS = True
        self.ADD_FINDVIEWBYID_IMPORTS = True
        self.PRESERVE_COMMENTS = True
        
    @classmethod
    def from_file(cls, config_path: str) -> 'Config':
        """从配置文件加载配置"""
        config = cls()
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 更新配置
                for key, value in config_data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
                        
            except Exception as e:
                print(f"警告: 加载配置文件失败: {e}")
        
        return config
    
    def save_to_file(self, config_path: str):
        """保存配置到文件"""
        try:
            config_data = {}
            for key in dir(self):
                if not key.startswith('_') and not callable(getattr(self, key)):
                    config_data[key] = getattr(self, key)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get_scan_paths(self) -> list:
        """获取需要扫描的完整路径列表"""
        scan_paths = []
        project_path = Path(self.PROJECT_PATH)
        
        for scan_dir in self.SCAN_DIRECTORIES:
            full_path = project_path / scan_dir
            if full_path.exists():
                scan_paths.append(str(full_path))
        
        # 如果没有找到指定的目录，添加项目根目录
        if not scan_paths:
            scan_paths.append(str(project_path))
        
        return scan_paths
    
    def get_exclude_patterns(self) -> list:
        """获取排除模式列表"""
        patterns = []
        
        # 添加目录排除模式
        for exclude_dir in self.EXCLUDE_DIRECTORIES:
            patterns.append(f"**/{exclude_dir}/**")
        
        # 添加文件排除模式
        for exclude_file in self.EXCLUDE_PATTERNS:
            patterns.append(f"**/{exclude_file}")
        
        return patterns
    
    def validate(self) -> bool:
        """验证配置的有效性"""
        if not os.path.exists(self.PROJECT_PATH):
            print(f"错误: 项目路径不存在: {self.PROJECT_PATH}")
            return False
        
        if self.BINDING_MODE not in ["findViewById", "viewBinding"]:
            print(f"错误: 无效的绑定模式: {self.BINDING_MODE}")
            return False
        
        if self.LOG_LEVEL not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            print(f"错误: 无效的日志级别: {self.LOG_LEVEL}")
            return False
        
        return True
    
    def __str__(self) -> str:
        """配置的字符串表示"""
        return f"""配置信息:
项目路径: {self.PROJECT_PATH}
绑定模式: {self.BINDING_MODE}
启用备份: {self.BACKUP_ENABLED}
日志级别: {self.LOG_LEVEL}
扫描扩展名: {', '.join(self.SCAN_EXTENSIONS)}
扫描目录: {', '.join(self.SCAN_DIRECTORIES)}
排除目录: {', '.join(self.EXCLUDE_DIRECTORIES)}
"""


# 默认配置文件路径
DEFAULT_CONFIG_PATH = "butterknife_migrator_config.json"


def create_default_config():
    """创建默认配置文件"""
    config = Config()
    config.save_to_file(DEFAULT_CONFIG_PATH)
    print(f"默认配置文件已创建: {DEFAULT_CONFIG_PATH}")


if __name__ == '__main__':
    create_default_config()
