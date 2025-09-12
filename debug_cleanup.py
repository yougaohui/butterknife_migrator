#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试清理逻辑问题
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from injector.code_injector import CodeInjector
from butterknife_parser_module.butterknife_parser import ButterKnifeParser

def debug_cleanup():
    """调试清理逻辑"""
    # 读取测试文件
    with open('tests/Agent_DeviceListActivity.java', 'r', encoding='utf-8') as f:
        original_code = f.read()
    
    print("原始代码长度:", len(original_code))
    
    # 解析ButterKnife注解
    parser = ButterKnifeParser()
    parsed_data = parser.parse(original_code)
    
    print("解析结果:")
    print(f"  - 有ButterKnife注解: {parsed_data['has_butterknife']}")
    print(f"  - BindView数量: {len(parsed_data.get('bind_views', []))}")
    print(f"  - OnClick数量: {len(parsed_data.get('on_clicks', []))}")
    
    # 使用代码注入器
    injector = CodeInjector()
    
    # 直接调用清理方法
    print("\n开始清理onCreate方法中重复的UI初始化代码...")
    result_code = injector._clean_duplicate_findview_in_oncreate(original_code, parsed_data)
    
    print("清理后代码长度:", len(result_code))
    
    # 检查第110行附近的内容
    lines = result_code.split('\n')
    print("\n第105-125行的内容:")
    for i in range(104, 125):
        if i < len(lines):
            print(f'{i+1:3d}: {lines[i].rstrip()}')
    
    # 检查是否有重复的findViewById代码
    findViewById_lines = []
    for i, line in enumerate(lines):
        if 'findViewById(' in line and '=' in line:
            findViewById_lines.append((i+1, line.strip()))
    
    print(f"\n找到 {len(findViewById_lines)} 行findViewById调用:")
    for line_num, line_content in findViewById_lines:
        print(f"  第{line_num}行: {line_content}")

if __name__ == '__main__':
    debug_cleanup()
