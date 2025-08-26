#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BindCall移除器
删除 ButterKnife.bind调用
删除相关 import 语句
"""

import re
from typing import Dict, Any
from .base_transformer import BaseTransformer


class BindCallRemover(BaseTransformer):
    """BindCall移除器类"""
    
    def __init__(self):
        super().__init__()
        self.description = "删除ButterKnife.bind调用和相关import语句"
        
        # 编译正则表达式
        self.bind_call_pattern = re.compile(
            r'\s*ButterKnife\.bind\s*\(\s*this\s*\)\s*;?\s*\n?',
            re.MULTILINE
        )
        
        self.butterknife_import_pattern = re.compile(
            r'import\s+butterknife\.ButterKnife\s*;\s*\n?',
            re.MULTILINE
        )
        
        self.bindview_import_pattern = re.compile(
            r'import\s+butterknife\.BindView\s*;\s*\n?',
            re.MULTILINE
        )
        
        self.onclick_import_pattern = re.compile(
            r'import\s+butterknife\.OnClick\s*;\s*\n?',
            re.MULTILINE
        )
        
        self.unbind_call_pattern = re.compile(
            r'\s*ButterKnife\.unbind\s*\(\s*this\s*\)\s*;?\s*\n?',
            re.MULTILINE
        )
    
    def can_transform(self, parsed_data: Dict[str, Any]) -> bool:
        """检查是否可以应用此转换器"""
        return (
            parsed_data.get('bind_call', False) or
            any(parsed_data.get('imports', {}).values())
        )
    
    def transform(self, parsed_data: Dict[str, Any], original_code: str) -> str:
        """删除ButterKnife相关的代码和import"""
        if not self.can_transform(parsed_data):
            return original_code
        
        transformed_code = original_code
        
        # 1. 删除ButterKnife.bind调用
        transformed_code = self._remove_bind_calls(transformed_code)
        
        # 2. 删除ButterKnife.unbind调用
        transformed_code = self._remove_unbind_calls(transformed_code)
        
        # 3. 删除ButterKnife相关的import语句
        transformed_code = self._remove_butterknife_imports(transformed_code)
        
        # 4. 清理多余的空行
        transformed_code = self._cleanup_empty_lines(transformed_code)
        
        return transformed_code
    
    def _remove_bind_calls(self, code: str) -> str:
        """删除ButterKnife.bind调用"""
        # 查找并删除ButterKnife.bind(this);调用
        lines = code.split('\n')
        filtered_lines = []
        
        for line in lines:
            # 跳过包含ButterKnife.bind的行
            if 'ButterKnife.bind' in line:
                continue
            
            # 跳过只包含分号或空白的行
            if line.strip() in ['', ';']:
                continue
            
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _remove_unbind_calls(self, code: str) -> str:
        """删除ButterKnife.unbind调用"""
        # 查找并删除ButterKnife.unbind(this);调用
        lines = code.split('\n')
        filtered_lines = []
        
        for line in lines:
            # 跳过包含ButterKnife.unbind的行
            if 'ButterKnife.unbind' in line:
                continue
            
            # 跳过只包含分号或空白的行
            if line.strip() in ['', ';']:
                continue
            
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _remove_butterknife_imports(self, code: str) -> str:
        """删除ButterKnife相关的import语句"""
        # 删除ButterKnife相关的import
        code = self.butterknife_import_pattern.sub('', code)
        code = self.bindview_import_pattern.sub('', code)
        code = self.onclick_import_pattern.sub('', code)
        
        return code
    
    def _cleanup_empty_lines(self, code: str) -> str:
        """清理多余的空行"""
        lines = code.split('\n')
        cleaned_lines = []
        prev_empty = False
        
        for line in lines:
            is_empty = line.strip() == ''
            
            if is_empty and prev_empty:
                # 跳过连续的空行
                continue
            
            cleaned_lines.append(line)
            prev_empty = is_empty
        
        # 移除开头和结尾的空行
        while cleaned_lines and cleaned_lines[0].strip() == '':
            cleaned_lines.pop(0)
        
        while cleaned_lines and cleaned_lines[-1].strip() == '':
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    def get_transformation_info(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取转换信息"""
        info = super().get_transformation_info(parsed_data)
        
        if self.can_transform(parsed_data):
            changes_count = 0
            
            if parsed_data.get('bind_call', False):
                changes_count += 1
            
            imports = parsed_data.get('imports', {})
            changes_count += sum(imports.values())
            
            info['changes_count'] = changes_count
            info['description'] = f"删除 {changes_count} 个ButterKnife相关元素"
        
        return info
    
    def get_removed_elements(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取被删除的元素信息"""
        removed = {
            'bind_calls': [],
            'unbind_calls': [],
            'imports': []
        }
        
        if parsed_data.get('bind_call', False):
            removed['bind_calls'].append('ButterKnife.bind(this);')
        
        imports = parsed_data.get('imports', {})
        if imports.get('butterknife', False):
            removed['imports'].append('import butterknife.ButterKnife;')
        
        if imports.get('bindview', False):
            removed['imports'].append('import butterknife.BindView;')
        
        if imports.get('onclick', False):
            removed['imports'].append('import butterknife.OnClick;')
        
        return removed
