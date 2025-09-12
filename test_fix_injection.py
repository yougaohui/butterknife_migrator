#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的代码注入器
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from injector.code_injector import CodeInjector
from butterknife_parser_module.butterknife_parser import ButterKnifeParser

def test_injection_fix():
    """测试代码注入修复"""
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
    result_code = injector.inject(original_code, parsed_data)
    
    print("注入后代码长度:", len(result_code))
    
    # 检查是否还有重复的findViewById代码
    lines = result_code.split('\n')
    findViewById_lines = []
    for i, line in enumerate(lines):
        if 'findViewById(' in line and 'listview =' in line:
            findViewById_lines.append((i+1, line.strip()))
    
    print(f"找到 {len(findViewById_lines)} 行listview的findViewById调用:")
    for line_num, line_content in findViewById_lines:
        print(f"  第{line_num}行: {line_content}")
    
    # 检查onCreate方法中的重复代码
    in_oncreate = False
    onCreate_findViewById_lines = []
    for i, line in enumerate(lines):
        if 'protected void onCreate(' in line:
            in_oncreate = True
            continue
        elif in_oncreate and line.strip() == '}':
            break
        elif in_oncreate and 'findViewById(' in line:
            onCreate_findViewById_lines.append((i+1, line.strip()))
    
    print(f"onCreate方法中找到 {len(onCreate_findViewById_lines)} 行findViewById调用:")
    for line_num, line_content in onCreate_findViewById_lines:
        print(f"  第{line_num}行: {line_content}")
    
    # 检查initViews方法
    in_initviews = False
    initviews_findViewById_lines = []
    for i, line in enumerate(lines):
        if 'protected void initViews()' in line:
            in_initviews = True
            continue
        elif in_initviews and line.strip() == '}':
            break
        elif in_initviews and 'findViewById(' in line:
            initviews_findViewById_lines.append((i+1, line.strip()))
    
    print(f"initViews方法中找到 {len(initviews_findViewById_lines)} 行findViewById调用:")
    for line_num, line_content in initviews_findViewById_lines:
        print(f"  第{line_num}行: {line_content}")

if __name__ == '__main__':
    test_injection_fix()
