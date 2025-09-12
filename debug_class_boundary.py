#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def _find_class_end(code: str) -> int:
    """查找主类的结束位置（排除内部类）"""
    # 首先找到主类的开始位置（支持public和默认访问修饰符）
    main_class_match = re.search(r'(?:public\s+)?class\s+\w+.*?\{', code, re.DOTALL)
    print(f"DEBUG: 主类匹配结果: {main_class_match}")
    if not main_class_match:
        print("DEBUG: 未找到主类定义")
        return -1
    
    # 从主类开始位置开始计算大括号
    start_pos = main_class_match.end() - 1  # 回到开括号位置
    print(f"DEBUG: 主类开始位置: {start_pos}")
    brace_count = 1
    in_string = False
    string_char = None
    in_comment = False
    in_single_line_comment = False
    
    for i in range(start_pos + 1, len(code)):
        char = code[i]
        
        # 处理单行注释
        if not in_string and not in_comment and not in_single_line_comment:
            if i < len(code) - 1 and code[i:i+2] == '//':
                in_single_line_comment = True
                continue
        elif in_single_line_comment:
            if char == '\n':
                in_single_line_comment = False
            continue
        
        # 处理多行注释
        if not in_string and not in_comment and not in_single_line_comment:
            if i < len(code) - 1 and code[i:i+2] == '/*':
                in_comment = True
                continue
        elif in_comment:
            if i < len(code) - 1 and code[i:i+2] == '*/':
                in_comment = False
                continue
            continue
        
        # 处理字符串字面量
        if char == '"' or char == "'":
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                in_string = False
                string_char = None
            continue
        
        if in_string or in_comment or in_single_line_comment:
            continue
        
        # 检查是否遇到内部类定义
        if char == '}':
            # 检查这个}是否是主类的结束
            if brace_count == 1:
                print(f"DEBUG: 找到可能的类结束位置: {i}, 剩余代码: {code[i+1:i+50]}")
                # 检查}后面是否还有内容（内部类）
                remaining_code = code[i+1:].strip()
                if remaining_code and not remaining_code.startswith('}'):
                    # 如果还有内容，检查是否是内部类
                    # 跳过空白字符和注释
                    j = i + 1
                    while j < len(code) and code[j] in ' \t\n\r':
                        j += 1
                    
                    # 检查是否是内部类定义
                    if j < len(code) - 1:
                        # 检查是否是class关键字
                        if (code[j:j+5] == 'class' or 
                            (j < len(code) - 10 and 'class' in code[j:j+10])):
                            print(f"DEBUG: 发现内部类，继续寻找主类结束")
                            # 这是内部类，继续寻找主类结束
                            brace_count -= 1
                            continue
                
                # 找到主类结束位置
                print(f"DEBUG: 找到主类结束位置: {i + 1}")
                return i + 1
            else:
                brace_count -= 1
        elif char == '{':
            brace_count += 1
    
    return -1

# 测试
with open('test_class_boundary.java', 'r', encoding='utf-8') as f:
    code = f.read()

print("测试代码:")
print(code)
print("\n" + "="*50 + "\n")

result = _find_class_end(code)
print(f"\n最终结果: {result}")

if result != -1:
    print(f"\n主类结束位置: {result}")
    print(f"主类结束前的内容: {code[result-20:result+20]}")
else:
    print("未找到主类结束位置")
