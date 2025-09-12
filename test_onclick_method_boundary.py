#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from butterknife_parser_module.butterknife_parser import ButterKnifeParser

def test_onclick_method_boundary():
    """测试Agent_DeviceListActivity中onClick方法的方法边界检测"""
    
    # 读取真实的Agent_DeviceListActivity文件
    with open('tests/Agent_DeviceListActivity.java', 'r', encoding='utf-8') as f:
        content = f.read()
    
    parser = ButterKnifeParser()
    
    print("=== 测试Agent_DeviceListActivity中的onClick方法边界检测 ===")
    
    # 测试方法边界检测
    method_start, method_end = parser._find_method_boundaries(content, "onClick")
    print(f"方法开始位置: {method_start}")
    print(f"方法结束位置: {method_end}")
    
    if method_start != -1 and method_end != -1:
        method_content = content[method_start:method_end]
        print(f"方法长度: {len(method_content)} 字符")
        print(f"方法行数: {method_content.count(chr(10)) + 1} 行")
        
        # 显示方法的前几行
        lines = method_content.split('\n')
        print(f"\n方法前10行:")
        for i, line in enumerate(lines[:10]):
            print(f"{i+1:3d}: {line}")
        
        # 显示方法的最后几行
        print(f"\n方法最后10行:")
        for i, line in enumerate(lines[-10:]):
            line_num = len(lines) - 10 + i + 1
            print(f"{line_num:3d}: {line}")
        
        # 检查方法中是否包含嵌套的onClick方法
        nested_onclick_count = method_content.count('public void onClick(')
        print(f"\n嵌套的onClick方法数量: {nested_onclick_count}")
        
        # 检查方法中是否包含switch语句
        switch_count = method_content.count('switch (')
        print(f"switch语句数量: {switch_count}")
        
        # 检查方法中是否包含注释掉的代码
        commented_code_count = method_content.count('/*') + method_content.count('*/')
        print(f"注释块数量: {commented_code_count // 2}")
        
        # 检查大括号匹配
        open_braces = method_content.count('{')
        close_braces = method_content.count('}')
        print(f"开括号数量: {open_braces}")
        print(f"闭括号数量: {close_braces}")
        print(f"大括号匹配: {'是' if open_braces == close_braces else '否'}")
    
    # 测试参数检测
    has_view_param, param_type = parser._check_method_has_view_param(content, "onClick")
    print(f"\n有View参数: {has_view_param}")
    print(f"参数类型: {param_type}")
    
    # 测试注释过滤
    filtered_content = parser._remove_commented_code(content)
    print(f"\n原始内容长度: {len(content)}")
    print(f"过滤后内容长度: {len(filtered_content)}")
    print(f"过滤掉的字符数: {len(content) - len(filtered_content)}")
    
    # 在过滤后的内容中再次测试方法边界检测
    filtered_method_start, filtered_method_end = parser._find_method_boundaries(filtered_content, "onClick")
    print(f"\n过滤后方法开始位置: {filtered_method_start}")
    print(f"过滤后方法结束位置: {filtered_method_end}")
    
    if filtered_method_start != -1 and filtered_method_end != -1:
        filtered_method_content = filtered_content[filtered_method_start:filtered_method_end]
        print(f"过滤后方法长度: {len(filtered_method_content)} 字符")
        print(f"过滤后方法行数: {filtered_method_content.count(chr(10)) + 1} 行")

if __name__ == "__main__":
    test_onclick_method_boundary()
