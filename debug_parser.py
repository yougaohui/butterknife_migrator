#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from butterknife_parser_module.butterknife_parser import ButterKnifeParser

def debug_parser():
    """调试解析器问题"""
    
    # 读取实际文件
    file_path = "tests/Agent_DeviceListActivity.java"
    with open(file_path, 'r', encoding='utf-8') as f:
        original_code = f.read()
    
    print("=== 检查文件内容 ===")
    lines = original_code.split('\n')
    for i, line in enumerate(lines[55:70], 56):  # 检查第56-70行
        print(f"{i:3d}: {line}")
    
    print("\n=== 检查@BindView注解 ===")
    bindview_lines = [line for line in lines if '@BindView' in line]
    print(f"找到{len(bindview_lines)}个@BindView注解:")
    for line in bindview_lines:
        print(f"  {line.strip()}")
    
    print("\n=== 检查@OnClick注解 ===")
    onclick_lines = [line for line in lines if '@OnClick' in line]
    print(f"找到{len(onclick_lines)}个@OnClick注解:")
    for line in onclick_lines:
        print(f"  {line.strip()}")
    
    print("\n=== 检查ButterKnife.bind调用 ===")
    bindcall_lines = [line for line in lines if 'ButterKnife.bind' in line]
    print(f"找到{len(bindcall_lines)}个ButterKnife.bind调用:")
    for line in bindcall_lines:
        print(f"  {line.strip()}")
    
    print("\n=== 测试解析器 ===")
    parser = ButterKnifeParser()
    parsed_data = parser.parse(original_code)
    
    print(f"解析结果:")
    print(f"  - @BindView注解数量: {len(parsed_data.get('bind_views', []))}")
    print(f"  - @OnClick注解数量: {len(parsed_data.get('on_clicks', []))}")
    print(f"  - ButterKnife.bind调用: {parsed_data.get('bind_call', False)}")
    
    if parsed_data.get('bind_views'):
        print(f"  - @BindView详情:")
        for i, bind_view in enumerate(parsed_data['bind_views']):
            print(f"    {i+1}. {bind_view['type']} {bind_view['name']} = {bind_view['id']}")

if __name__ == "__main__":
    debug_parser()
