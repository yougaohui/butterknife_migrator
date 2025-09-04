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
        
        # 只替换@BindView注解为普通字段声明
        for bind_view in bind_views:
            transformed_code = self._replace_bind_view_annotation(
                transformed_code, bind_view
            )
        
        return transformed_code
    
    def _replace_bind_view_annotation(self, code: str, bind_view: Dict[str, Any]) -> str:
        """替换@BindView注解为普通字段声明"""
        field_type = bind_view['type']
        field_name = bind_view['name']
        resource_id = bind_view['id']
        
        # 查找@BindView注解行（支持多行格式和修饰符）
        escaped_resource_id = re.escape(resource_id)
        escaped_field_type = re.escape(field_type)
        escaped_field_name = re.escape(field_name)
        pattern = re.compile(
            r'@BindView\s*\(\s*' + escaped_resource_id + r'\s*\)\s*\n\s*(?:public\s+|private\s+|protected\s+)?' + escaped_field_type + r'\s+' + escaped_field_name + r'\s*;',
            re.MULTILINE | re.DOTALL
        )
        
        # 替换为普通字段声明
        replacement = f"{field_type} {field_name};"
        
        return pattern.sub(replacement, code)
    
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
        # 查找类的结束位置
        class_end_pattern = re.compile(r'(\s*)\}\s*$', re.MULTILINE)
        
        match = class_end_pattern.search(code)
        if match:
            # 在类结束前添加初始化方法
            method_code = f"""
    private void initializeViews() {{
{initialization_code}
    }}
"""
            
            before_end = code[:match.start()]
            after_end = code[match.start():]
            
            return before_end + method_code + after_end
        
        return code
    
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
