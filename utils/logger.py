#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志工具模块
控制台输出 + 文件日志
支持 debug/info/warning/error 等级
"""

import os
import sys
from datetime import datetime
from typing import Optional, TextIO
from config import Config


class Logger:
    """日志记录器类"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.log_file = None
        self.log_level = self._get_log_level()
        
        # 初始化日志文件
        if self.config.LOG_FILE:
            self._init_log_file()
    
    def _get_log_level(self) -> int:
        """获取日志级别数值"""
        level_map = {
            'DEBUG': 0,
            'INFO': 1,
            'WARNING': 2,
            'ERROR': 3
        }
        
        return level_map.get(self.config.LOG_LEVEL.upper(), 1)
    
    def _init_log_file(self):
        """初始化日志文件"""
        try:
            log_path = os.path.join(self.config.PROJECT_PATH, self.config.LOG_FILE)
            log_dir = os.path.dirname(log_path)
            
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            self.log_file = open(log_path, 'a', encoding='utf-8')
            
        except Exception as e:
            print(f"初始化日志文件失败: {e}")
            self.log_file = None
    
    def _should_log(self, level: str) -> bool:
        """检查是否应该记录该级别的日志"""
        level_map = {
            'DEBUG': 0,
            'INFO': 1,
            'WARNING': 2,
            'ERROR': 3
        }
        
        return level_map.get(level.upper(), 1) >= self.log_level
    
    def _format_message(self, level: str, message: str) -> str:
        """格式化日志消息"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"[{timestamp}] [{level.upper()}] {message}"
    
    def _write_log(self, level: str, message: str):
        """写入日志"""
        if not self._should_log(level):
            return
        
        formatted_message = self._format_message(level, message)
        
        # 控制台输出
        if level.upper() == 'ERROR':
            print(formatted_message, file=sys.stderr)
        else:
            print(formatted_message)
        
        # 文件日志
        if self.log_file:
            try:
                self.log_file.write(formatted_message + '\n')
                self.log_file.flush()
            except Exception as e:
                print(f"写入日志文件失败: {e}")
    
    def debug(self, message: str):
        """记录调试信息"""
        self._write_log('DEBUG', message)
    
    def info(self, message: str):
        """记录一般信息"""
        self._write_log('INFO', message)
    
    def warning(self, message: str):
        """记录警告信息"""
        self._write_log('WARNING', message)
    
    def error(self, message: str):
        """记录错误信息"""
        self._write_log('ERROR', message)
    
    def critical(self, message: str):
        """记录严重错误信息"""
        self._write_log('ERROR', f"CRITICAL: {message}")
    
    def log(self, level: str, message: str):
        """通用日志方法"""
        self._write_log(level, message)
    
    def log_exception(self, message: str, exception: Exception = None):
        """记录异常信息"""
        if exception:
            error_msg = f"{message}: {type(exception).__name__}: {str(exception)}"
        else:
            error_msg = message
        
        self.error(error_msg)
        
        # 如果是调试模式，记录完整的异常堆栈
        if self.log_level <= 0 and exception:
            import traceback
            self.debug(f"异常堆栈:\n{traceback.format_exc()}")
    
    def log_progress(self, current: int, total: int, description: str = ""):
        """记录进度信息"""
        if total > 0:
            percentage = (current / total) * 100
            progress_msg = f"进度: {current}/{total} ({percentage:.1f}%)"
            
            if description:
                progress_msg += f" - {description}"
            
            self.info(progress_msg)
    
    def log_file_operation(self, operation: str, file_path: str, success: bool, details: str = ""):
        """记录文件操作日志"""
        status = "成功" if success else "失败"
        message = f"文件操作 {operation}: {os.path.basename(file_path)} - {status}"
        
        if details:
            message += f" ({details})"
        
        if success:
            self.info(message)
        else:
            self.error(message)
    
    def log_migration_step(self, step: str, details: str = "", success: bool = True):
        """记录迁移步骤日志"""
        status = "完成" if success else "失败"
        message = f"迁移步骤: {step} - {status}"
        
        if details:
            message += f" - {details}"
        
        if success:
            self.info(message)
        else:
            self.error(message)
    
    def log_statistics(self, stats: dict, title: str = "统计信息"):
        """记录统计信息"""
        self.info(f"=== {title} ===")
        
        for key, value in stats.items():
            if isinstance(value, (int, float)):
                if isinstance(value, float):
                    formatted_value = f"{value:.2f}"
                else:
                    formatted_value = str(value)
                
                self.info(f"  {key}: {formatted_value}")
            else:
                self.info(f"  {key}: {value}")
        
        self.info("=" * (len(title) + 8))
    
    def set_log_level(self, level: str):
        """设置日志级别"""
        old_level = self.log_level
        self.log_level = self._get_log_level()
        
        if old_level != self.log_level:
            self.info(f"日志级别已更改: {level.upper()}")
    
    def get_log_level_name(self) -> str:
        """获取当前日志级别名称"""
        level_names = {
            0: 'DEBUG',
            1: 'INFO',
            2: 'WARNING',
            3: 'ERROR'
        }
        
        return level_names.get(self.log_level, 'INFO')
    
    def is_debug_enabled(self) -> bool:
        """检查是否启用调试模式"""
        return self.log_level <= 0
    
    def is_info_enabled(self) -> bool:
        """检查是否启用信息模式"""
        return self.log_level <= 1
    
    def is_warning_enabled(self) -> bool:
        """检查是否启用警告模式"""
        return self.log_level <= 2
    
    def is_error_enabled(self) -> bool:
        """检查是否启用错误模式"""
        return self.log_level <= 3
    
    def close(self):
        """关闭日志文件"""
        if self.log_file:
            try:
                self.log_file.close()
                self.log_file = None
            except Exception as e:
                print(f"关闭日志文件失败: {e}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
    
    def __del__(self):
        """析构函数"""
        self.close()


class ColoredLogger(Logger):
    """带颜色的日志记录器"""
    
    def __init__(self, config: Optional[Config] = None):
        super().__init__(config)
        self.colors = {
            'DEBUG': '\033[36m',    # 青色
            'INFO': '\033[32m',     # 绿色
            'WARNING': '\033[33m',  # 黄色
            'ERROR': '\033[31m',    # 红色
            'RESET': '\033[0m'      # 重置
        }
    
    def _write_log(self, level: str, message: str):
        """写入带颜色的日志"""
        if not self._should_log(level):
            return
        
        formatted_message = self._format_message(level, message)
        
        # 控制台输出（带颜色）
        if level.upper() == 'ERROR':
            colored_message = f"{self.colors['ERROR']}{formatted_message}{self.colors['RESET']}"
            print(colored_message, file=sys.stderr)
        else:
            color = self.colors.get(level.upper(), self.colors['RESET'])
            colored_message = f"{color}{formatted_message}{self.colors['RESET']}"
            print(colored_message)
        
        # 文件日志（不带颜色）
        if self.log_file:
            try:
                self.log_file.write(formatted_message + '\n')
                self.log_file.flush()
            except Exception as e:
                print(f"写入日志文件失败: {e}")


# 全局日志记录器实例
_global_logger = None


def get_logger(config: Optional[Config] = None) -> Logger:
    """获取全局日志记录器"""
    global _global_logger
    
    if _global_logger is None:
        _global_logger = Logger(config)
    
    return _global_logger


def set_global_logger(logger: Logger):
    """设置全局日志记录器"""
    global _global_logger
    _global_logger = logger


def log_debug(message: str):
    """全局调试日志"""
    get_logger().debug(message)


def log_info(message: str):
    """全局信息日志"""
    get_logger().info(message)


def log_warning(message: str):
    """全局警告日志"""
    get_logger().warning(message)


def log_error(message: str):
    """全局错误日志"""
    get_logger().error(message)
