#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码格式化器
在ButterKnife迁移前统一格式化代码，解决缩进和换行问题
"""

import re
from typing import List, Tuple


class CodeFormatter:
    """代码格式化器类"""
    
    def __init__(self):
        # 匹配@BindView注解在同一行的情况
        self.bindview_same_line_pattern = re.compile(
            r'(\s*)@BindView\s*\(\s*([^)]+)\s*\)\s+(\w+)\s+(\w+)\s*;',
            re.MULTILINE
        )
        
        # 匹配@OnClick注解在同一行的情况
        self.onclick_same_line_pattern = re.compile(
            r'(\s*)@OnClick\s*\(\s*([^)]+)\s*\)\s+(?:public\s+)?(?:void\s+)?(\w+)\s*\([^)]*\)',
            re.MULTILINE
        )
        
        # 匹配@OnLongClick注解在同一行的情况
        self.onlongclick_same_line_pattern = re.compile(
            r'(\s*)@OnLongClick\s*\(\s*([^)]+)\s*\)\s+(?:public\s+)?(?:boolean\s+)?(\w+)\s*\([^)]*\)',
            re.MULTILINE
        )
    
    def format_butterknife_annotations(self, content: str) -> str:
        """格式化ButterKnife注解，将同一行的注解分离到不同行"""
        formatted_content = content
        
        # 格式化@BindView注解
        formatted_content = self._format_bindview_annotations(formatted_content)
        
        # 格式化@OnClick注解
        formatted_content = self._format_onclick_annotations(formatted_content)
        
        # 格式化@OnLongClick注解
        formatted_content = self._format_onlongclick_annotations(formatted_content)
        
        return formatted_content
    
    def _format_bindview_annotations(self, content: str) -> str:
        """格式化@BindView注解"""
        def replace_bindview(match):
            indent = match.group(1)
            resource_id = match.group(2)
            field_type = match.group(3)
            field_name = match.group(4)
            
            # 分离注解和变量声明
            return f"{indent}@BindView({resource_id})\n{indent}{field_type} {field_name};"
        
        return self.bindview_same_line_pattern.sub(replace_bindview, content)
    
    def _format_onclick_annotations(self, content: str) -> str:
        """格式化@OnClick注解"""
        def replace_onclick(match):
            indent = match.group(1)
            resource_ids = match.group(2)
            method_name = match.group(3)
            
            # 查找完整的方法定义
            method_def = self._find_complete_method_definition(content, match.start(), method_name)
            if method_def:
                # 分离注解和方法定义
                return f"{indent}@OnClick({resource_ids})\n{method_def}"
            else:
                # 如果找不到完整方法定义，保持原样
                return match.group(0)
        
        return self.onclick_same_line_pattern.sub(replace_onclick, content)
    
    def _format_onlongclick_annotations(self, content: str) -> str:
        """格式化@OnLongClick注解"""
        def replace_onlongclick(match):
            indent = match.group(1)
            resource_ids = match.group(2)
            method_name = match.group(3)
            
            # 查找完整的方法定义
            method_def = self._find_complete_method_definition(content, match.start(), method_name)
            if method_def:
                # 分离注解和方法定义
                return f"{indent}@OnLongClick({resource_ids})\n{method_def}"
            else:
                # 如果找不到完整方法定义，保持原样
                return match.group(0)
        
        return self.onlongclick_same_line_pattern.sub(replace_onlongclick, content)
    
    def _find_complete_method_definition(self, content: str, start_pos: int, method_name: str) -> str:
        """查找完整的方法定义"""
        # 从匹配位置开始查找方法定义
        lines = content[start_pos:].split('\n')
        
        for i, line in enumerate(lines):
            if method_name in line and '(' in line:
                # 找到方法定义行，需要包含完整的方法签名
                method_lines = [line]
                
                # 如果方法定义跨多行，继续查找
                j = i + 1
                while j < len(lines) and '{' not in lines[j-1]:
                    method_lines.append(lines[j])
                    j += 1
                
                # 添加方法体开始的大括号
                if j < len(lines) and '{' in lines[j]:
                    method_lines.append(lines[j])
                
                return '\n'.join(method_lines)
        
        return None
    
    def normalize_whitespace(self, content: str) -> str:
        """标准化空白字符"""
        # 将制表符转换为4个空格
        content = content.replace('\t', '    ')
        
        # 移除行尾空白
        lines = content.split('\n')
        normalized_lines = [line.rstrip() for line in lines]
        
        return '\n'.join(normalized_lines)
    
    def format_imports(self, content: str) -> str:
        """格式化import语句，确保它们按正确顺序排列"""
        lines = content.split('\n')
        import_lines = []
        other_lines = []
        in_imports = True
        
        for line in lines:
            stripped = line.strip()
            if in_imports and stripped.startswith('import '):
                import_lines.append(line)
            elif stripped == '' and in_imports:
                # 空行，继续在imports区域
                import_lines.append(line)
            else:
                in_imports = False
                other_lines.append(line)
        
        # 对import语句进行排序
        import_lines.sort(key=lambda x: x.strip())
        
        # 重新组合内容
        result_lines = import_lines + other_lines
        return '\n'.join(result_lines)
    
    def format_class_fields(self, content: str) -> str:
        """格式化类字段，确保正确的缩进"""
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # 如果是字段声明（包含@BindView或变量声明），确保正确的缩进
            if (stripped.startswith('@BindView') or 
                (stripped and not stripped.startswith('//') and 
                 not stripped.startswith('/*') and 
                 not stripped.startswith('*') and
                 not stripped.startswith('*/') and
                 not stripped.startswith('import ') and
                 not stripped.startswith('package ') and
                 not stripped.startswith('public class') and
                 not stripped.startswith('private ') and
                 not stripped.startswith('protected ') and
                 ';' in stripped and
                 not stripped.startswith('//'))):
                
                # 确保字段有正确的缩进（4个空格）
                if not line.startswith('    '):
                    line = '    ' + line.lstrip()
            
            formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def format_entire_file(self, content: str) -> str:
        """格式化整个文件"""
        # 1. 标准化空白字符
        formatted = self.normalize_whitespace(content)
        
        # 2. 格式化ButterKnife注解
        formatted = self.format_butterknife_annotations(formatted)
        
        # 3. 格式化import语句
        formatted = self.format_imports(formatted)
        
        # 4. 格式化类字段
        formatted = self.format_class_fields(formatted)
        
        return formatted
    
    def detect_formatting_issues(self, content: str) -> List[str]:
        """检测格式化问题"""
        issues = []
        
        # 检查@BindView注解是否在同一行
        bindview_matches = self.bindview_same_line_pattern.findall(content)
        if bindview_matches:
            issues.append(f"发现 {len(bindview_matches)} 个@BindView注解在同一行，需要格式化")
        
        # 检查@OnClick注解是否在同一行
        onclick_matches = self.onclick_same_line_pattern.findall(content)
        if onclick_matches:
            issues.append(f"发现 {len(onclick_matches)} 个@OnClick注解在同一行，需要格式化")
        
        # 检查@OnLongClick注解是否在同一行
        onlongclick_matches = self.onlongclick_same_line_pattern.findall(content)
        if onlongclick_matches:
            issues.append(f"发现 {len(onlongclick_matches)} 个@OnLongClick注解在同一行，需要格式化")
        
        return issues


def format_java_file(file_path: str) -> bool:
    """格式化Java文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        formatter = CodeFormatter()
        
        # 检测格式化问题
        issues = formatter.detect_formatting_issues(content)
        if not issues:
            print(f"文件 {file_path} 无需格式化")
            return True
        
        print(f"发现格式化问题: {', '.join(issues)}")
        
        # 格式化文件
        formatted_content = formatter.format_entire_file(content)
        
        # 如果内容有变化，写回文件
        if formatted_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            print(f"文件 {file_path} 格式化完成")
            return True
        else:
            print(f"文件 {file_path} 格式化后无变化")
            return True
            
    except Exception as e:
        print(f"格式化文件 {file_path} 时出错: {e}")
        return False


if __name__ == "__main__":
    # 测试代码
    test_content = """
    @BindView(R.id.listview) ListView listview;
    @BindView(R.id.tvAll) TextView tvAll;
    @OnClick(R.id.button) void onClick() {
        // method body
    }
    """
    
    formatter = CodeFormatter()
    formatted = formatter.format_entire_file(test_content)
    print("原始内容:")
    print(test_content)
    print("\n格式化后:")
    print(formatted)
