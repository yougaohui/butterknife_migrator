#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from injector.code_injector import CodeInjector

def test_class_boundary_detection():
    """测试类边界检测"""
    
    # 读取实际文件
    file_path = "tests/Agent_DeviceListActivity.java"
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    print("=== 测试类边界检测 ===")
    
    # 创建代码注入器
    injector = CodeInjector()
    
    # 测试类边界检测
    class_end = injector._find_class_end(code)
    print(f"检测到的类结束位置: {class_end}")
    
    if class_end != -1:
        # 显示类结束位置附近的内容
        start = max(0, class_end - 100)
        end = min(len(code), class_end + 100)
        print(f"类结束位置附近的内容:")
        print("=" * 50)
        print(code[start:end])
        print("=" * 50)
        
        # 检查是否有内部类
        inner_classes = code.count('class ')
        print(f"文件中class关键字数量: {inner_classes}")
        
        if inner_classes > 1:
            print("检测到内部类，这可能是导致边界检测问题的原因")
    else:
        print("未找到类结束位置")

if __name__ == "__main__":
    test_class_boundary_detection()
