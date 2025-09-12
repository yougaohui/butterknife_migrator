#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from butterknife_parser_module.butterknife_parser import ButterKnifeParser

def test_complex_onclick_structure():
    """测试复杂onClick方法中的各种嵌套结构"""
    
    # 读取真实的Agent_DeviceListActivity文件
    with open('tests/Agent_DeviceListActivity.java', 'r', encoding='utf-8') as f:
        content = f.read()
    
    parser = ButterKnifeParser()
    
    print("=== 测试复杂onClick方法中的嵌套结构 ===")
    
    # 获取onClick方法的内容
    method_start, method_end = parser._find_method_boundaries(content, "onClick")
    if method_start == -1 or method_end == -1:
        print("❌ 无法找到onClick方法")
        return
    
    method_content = content[method_start:method_end]
    lines = method_content.split('\n')
    
    print(f"✅ 找到onClick方法，位置: {method_start}-{method_end}")
    print(f"✅ 方法长度: {len(method_content)} 字符，{len(lines)} 行")
    
    # 分析嵌套结构
    print(f"\n=== 嵌套结构分析 ===")
    
    # 1. 分析switch语句
    switch_lines = []
    for i, line in enumerate(lines):
        if 'switch (' in line:
            switch_lines.append((i+1, line.strip()))
    
    print(f"✅ 找到 {len(switch_lines)} 个switch语句:")
    for line_num, line in switch_lines:
        print(f"   第{line_num}行: {line}")
    
    # 2. 分析case语句
    case_lines = []
    for i, line in enumerate(lines):
        if line.strip().startswith('case ') and ':' in line:
            case_lines.append((i+1, line.strip()))
    
    print(f"✅ 找到 {len(case_lines)} 个case语句:")
    for line_num, line in case_lines[:10]:  # 只显示前10个
        print(f"   第{line_num}行: {line}")
    if len(case_lines) > 10:
        print(f"   ... 还有 {len(case_lines) - 10} 个case语句")
    
    # 3. 分析嵌套的onClick方法
    nested_onclick_lines = []
    for i, line in enumerate(lines):
        if 'public void onClick(' in line and 'DialogInterface' in line:
            nested_onclick_lines.append((i+1, line.strip()))
    
    print(f"✅ 找到 {len(nested_onclick_lines)} 个嵌套的onClick方法:")
    for line_num, line in nested_onclick_lines:
        print(f"   第{line_num}行: {line}")
    
    # 4. 分析注释掉的代码
    commented_blocks = []
    in_comment = False
    comment_start = 0
    
    for i, line in enumerate(lines):
        if '/*' in line and not in_comment:
            in_comment = True
            comment_start = i + 1
        elif '*/' in line and in_comment:
            in_comment = False
            commented_blocks.append((comment_start, i + 1))
    
    print(f"✅ 找到 {len(commented_blocks)} 个注释块:")
    for start, end in commented_blocks:
        print(f"   第{start}-{end}行: 注释块")
    
    # 5. 分析大括号嵌套深度
    max_depth = 0
    current_depth = 0
    depth_changes = []
    
    for i, line in enumerate(lines):
        for char in line:
            if char == '{':
                current_depth += 1
                if current_depth > max_depth:
                    max_depth = current_depth
                    depth_changes.append((i+1, current_depth, 'open'))
            elif char == '}':
                current_depth -= 1
                if current_depth == 0:
                    depth_changes.append((i+1, current_depth, 'close'))
    
    print(f"✅ 最大嵌套深度: {max_depth}")
    print(f"✅ 大括号最终平衡: {'是' if current_depth == 0 else '否'}")
    
    # 6. 测试方法边界检测的准确性
    print(f"\n=== 方法边界检测准确性测试 ===")
    
    # 检查方法开始是否正确
    first_line = lines[0].strip()
    if first_line.startswith('public void onClick(View view) {'):
        print("✅ 方法开始检测正确")
    else:
        print(f"❌ 方法开始检测错误: {first_line}")
    
    # 检查方法结束是否正确
    last_line = lines[-1].strip()
    if last_line == '}':
        print("✅ 方法结束检测正确")
    else:
        print(f"❌ 方法结束检测错误: {last_line}")
    
    # 检查是否包含了完整的switch语句
    switch_start = -1
    switch_end = -1
    for i, line in enumerate(lines):
        if 'switch (view.getId()) {' in line:
            switch_start = i
        elif line.strip() == '}' and switch_start != -1:
            switch_end = i
            break
    
    if switch_start != -1 and switch_end != -1:
        print(f"✅ 包含完整的switch语句: 第{switch_start+1}-{switch_end+1}行")
    else:
        print("❌ switch语句检测不完整")
    
    # 7. 测试注释过滤后的效果
    print(f"\n=== 注释过滤效果测试 ===")
    
    filtered_content = parser._remove_commented_code(method_content)
    filtered_lines = filtered_content.split('\n')
    
    print(f"✅ 原始行数: {len(lines)}")
    print(f"✅ 过滤后行数: {len(filtered_lines)}")
    print(f"✅ 过滤掉的行数: {len(lines) - len(filtered_lines)}")
    
    # 在过滤后的内容中再次测试方法边界检测
    filtered_method_start, filtered_method_end = parser._find_method_boundaries(filtered_content, "onClick")
    if filtered_method_start != -1 and filtered_method_end != -1:
        print("✅ 过滤后方法边界检测仍然正确")
    else:
        print("❌ 过滤后方法边界检测失败")

if __name__ == "__main__":
    test_complex_onclick_structure()
