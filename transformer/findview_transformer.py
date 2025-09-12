#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FindView转换器
将 @BindView 替换为字段声明 + findViewById 初始化
"""

import re
from typing import Dict, Any, List
from .base_transformer import BaseTransformer


class FindViewTransformer(BaseTransformer):
    """FindView转换器类"""
    
    def __init__(self):
        super().__init__()
        self.description = "将@BindView注解转换为findViewById调用"
        
        # 编译正则表达式
        self.bind_view_pattern = re.compile(
            r'@BindView\s*\(\s*(R\.id\.\w+)\s*\)\s*\n\s*(?:public\s+|private\s+|protected\s+)?(\w+)\s+(\w+)\s*;',
            re.MULTILINE | re.DOTALL
        )
        
        self.field_declaration_pattern = re.compile(
            r'(\s*)(\w+)\s+(\w+)\s*;',
            re.MULTILINE
        )
    
    def can_transform(self, parsed_data: Dict[str, Any]) -> bool:
        """检查是否可以应用此转换器"""
        return len(parsed_data.get('bind_views', [])) > 0
    
    def transform(self, parsed_data: Dict[str, Any], original_code: str) -> str:
        """转换@BindView注解"""
        if not self.can_transform(parsed_data):
            return original_code
        
        transformed_code = original_code
        bind_views = parsed_data.get('bind_views', [])
        
        # 替换@BindView注解为普通字段声明
        for bind_view in bind_views:
            transformed_code = self._replace_bind_view_annotation(
                transformed_code, bind_view
            )
        
        # 添加findViewById初始化代码
        transformed_code = self._add_findviewbyid_initialization(transformed_code, bind_views)
        
        return transformed_code
    
    def _replace_bind_view_annotation(self, code: str, bind_view: Dict[str, Any]) -> str:
        """替换@BindView注解为普通字段声明"""
        field_type = bind_view['type']
        field_name = bind_view['name']
        resource_id = bind_view['id']
        
        # 查找@BindView注解行（支持同一行和多行格式）
        escaped_resource_id = re.escape(resource_id)
        escaped_field_type = re.escape(field_type)
        escaped_field_name = re.escape(field_name)
        
        # 模式1：同一行的格式 @BindView(R.id.xxx) Type fieldName;
        pattern1 = re.compile(
            r'@BindView\s*\(\s*' + escaped_resource_id + r'\s*\)\s+(?:public\s+|private\s+|protected\s+)?' + escaped_field_type + r'\s+' + escaped_field_name + r'\s*;',
            re.MULTILINE
        )
        
        # 模式2：多行的格式
        pattern2 = re.compile(
            r'@BindView\s*\(\s*' + escaped_resource_id + r'\s*\)\s*\n\s*(?:public\s+|private\s+|protected\s+)?' + escaped_field_type + r'\s+' + escaped_field_name + r'\s*;',
            re.MULTILINE | re.DOTALL
        )
        
        # 替换为普通字段声明
        replacement = f"{field_type} {field_name};"
        
        # 先尝试模式1（同一行）
        result = pattern1.sub(replacement, code)
        if result != code:
            return result
        
        # 再尝试模式2（多行）
        result = pattern2.sub(replacement, code)
        return result
    
    def _add_findviewbyid_initialization(self, code: str, bind_views: List[Dict[str, Any]]) -> str:
        """添加findViewById初始化代码"""
        if not bind_views:
            return code
        
        # 查找合适的方法来插入初始化代码
        initialization_code = self._generate_initialization_code(bind_views)
        
        # 尝试在onCreate方法中插入
        code = self._insert_in_oncreate(code, initialization_code)
        
        # 如果没有onCreate方法，尝试在onViewCreated方法中插入
        if not self._has_initialization_code(code, bind_views):
            code = self._insert_in_onviewcreated(code, initialization_code)
        
        # 如果还是没有找到合适的方法，在类的末尾添加一个初始化方法
        if not self._has_initialization_code(code, bind_views):
            code = self._add_initialization_method(code, initialization_code)
        
        return code
    
    def _generate_initialization_code(self, bind_views: List[Dict[str, Any]]) -> str:
        """生成初始化代码"""
        lines = []
        
        for bind_view in bind_views:
            field_name = bind_view['name']
            resource_id = bind_view['id']
            field_type = bind_view['type']
            
            # 生成findViewById调用
            line = f"        {field_name} = ({field_type}) findViewById({resource_id});"
            lines.append(line)
        
        return '\n'.join(lines)
    
    def _insert_in_oncreate(self, code: str, initialization_code: str) -> str:
        """在onCreate方法中插入初始化代码"""
        # 查找onCreate方法
        onCreate_pattern = re.compile(
            r'(\s*@Override\s*\n\s*protected\s+void\s+onCreate\s*\([^)]*\)\s*\{)',
            re.MULTILINE
        )
        
        match = onCreate_pattern.search(code)
        if match:
            # 在onCreate方法开始后插入初始化代码
            insert_position = match.end()
            
            # 查找方法体的结束位置
            brace_count = 0
            start_pos = insert_position
            
            for i, char in enumerate(code[start_pos:], start_pos):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # 找到方法体结束位置
                        insert_position = i
                        break
            
            # 在方法体结束前插入初始化代码
            if insert_position > start_pos:
                before_insert = code[:insert_position]
                after_insert = code[insert_position:]
                
                # 检查是否已经有初始化代码
                if not self._has_initialization_code(before_insert, []):
                    return before_insert + '\n        ' + initialization_code + '\n    ' + after_insert
        
        return code
    
    def _insert_in_onviewcreated(self, code: str, initialization_code: str) -> str:
        """在onViewCreated方法中插入初始化代码"""
        # 查找onViewCreated方法
        onViewCreated_pattern = re.compile(
            r'(\s*@Override\s*\n\s*public\s+void\s+onViewCreated\s*\([^)]*\)\s*\{)',
            re.MULTILINE
        )
        
        match = onViewCreated_pattern.search(code)
        if match:
            # 在onViewCreated方法开始后插入初始化代码
            insert_position = match.end()
            
            # 查找方法体的结束位置
            brace_count = 0
            start_pos = insert_position
            
            for i, char in enumerate(code[start_pos:], start_pos):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # 找到方法体结束位置
                        insert_position = i
                        break
            
            # 在方法体结束前插入初始化代码
            if insert_position > start_pos:
                before_insert = code[:insert_position]
                after_insert = code[insert_position:]
                
                # 检查是否已经有初始化代码
                if not self._has_initialization_code(before_insert, []):
                    return before_insert + '\n' + initialization_code + '\n    ' + after_insert
        
        return code
    
    def _add_initialization_method(self, code: str, initialization_code: str) -> str:
        """添加初始化方法"""
        # 查找主类的结束位置（排除内部类）
        main_class_end = self._find_main_class_end(code)
        
        if main_class_end != -1:
            # 在类结束前添加初始化方法
            method_code = f"""
    private void initViews() {{
{initialization_code}
    }}
"""
            
            before_end = code[:main_class_end]
            after_end = code[main_class_end:]
            
            return before_end + method_code + after_end
        
        return code
    
    def _find_main_class_end(self, code: str) -> int:
        """查找主类的结束位置，排除内部类"""
        lines = code.split('\n')
        brace_count = 0
        in_main_class = False
        main_class_start = -1
        
        # 查找主类开始位置
        for i, line in enumerate(lines):
            if re.match(r'\s*public\s+class\s+\w+', line):
                main_class_start = i
                break
        
        if main_class_start == -1:
            return -1
        
        # 从主类开始位置计算大括号
        for i in range(main_class_start, len(lines)):
            line = lines[i]
            
            # 计算大括号
            for char in line:
                if char == '{':
                    brace_count += 1
                    if brace_count == 1:
                        in_main_class = True
                elif char == '}':
                    brace_count -= 1
                    if in_main_class and brace_count == 0:
                        # 找到主类结束位置
                        return sum(len(lines[j]) + 1 for j in range(i + 1))
        
        return -1
    
    def _has_initialization_code(self, code: str, bind_views: List[Dict[str, Any]]) -> bool:
        """检查是否已经包含初始化代码"""
        if not bind_views:
            return False
        
        # 检查是否已经有findViewById调用
        for bind_view in bind_views:
            field_name = bind_view['name']
            resource_id = bind_view['id']
            
            escaped_field_name = re.escape(field_name)
            escaped_resource_id = re.escape(resource_id)
            pattern = escaped_field_name + r'\s*=\s*.*findViewById\s*\(\s*' + escaped_resource_id + r'\s*\)'
            if re.search(pattern, code, re.MULTILINE):
                return True
        
        return False
    
    def get_transformation_info(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取转换信息"""
        info = super().get_transformation_info(parsed_data)
        
        if self.can_transform(parsed_data):
            bind_views = parsed_data.get('bind_views', [])
            info['changes_count'] = len(bind_views)
            info['description'] = f"转换 {len(bind_views)} 个@BindView注解"
        
        return info
