#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OnClick转换器
将 @OnClick 替换为 setOnClickListener
"""

import re
from typing import Dict, Any, List
from .base_transformer import BaseTransformer


class OnClickTransformer(BaseTransformer):
    """OnClick转换器类"""
    
    def __init__(self):
        super().__init__()
        self.description = "将@OnClick注解转换为setOnClickListener调用"
        
        # 编译正则表达式
        self.on_click_pattern = re.compile(
            r'@OnClick\s*\(\s*\{\s*((?:R\.id\.\w+(?:\s*,\s*R\.id\.\w+)*)?)\s*\}\s*\)\s*public\s+void\s+(\w+)\s*\([^)]*\)\s*\{',
            re.MULTILINE
        )
        
        self.on_click_method_pattern = re.compile(
            r'@OnClick\s*\(\s*\{\s*((?:R\.id\.\w+(?:\s*,\s*R\.id\.\w+)*)?)\s*\}\s*\)\s*public\s+void\s+(\w+)\s*\([^)]*\)\s*\{[^}]*\}',
            re.MULTILINE | re.DOTALL
        )
    
    def can_transform(self, parsed_data: Dict[str, Any]) -> bool:
        """检查是否可以应用此转换器"""
        return len(parsed_data.get('on_clicks', [])) > 0
    
    def transform(self, parsed_data: Dict[str, Any], original_code: str) -> str:
        """转换@OnClick注解"""
        if not self.can_transform(parsed_data):
            return original_code
        
        transformed_code = original_code
        on_clicks = parsed_data.get('on_clicks', [])
        
        # 1. 替换@OnClick注解为setOnClickListener调用
        for on_click in on_clicks:
            transformed_code = self._replace_on_click_annotation(
                transformed_code, on_click
            )
        
        # 2. 添加setOnClickListener初始化代码
        transformed_code = self._add_onclick_listener_initialization(
            transformed_code, on_clicks
        )
        
        return transformed_code
    
    def _replace_on_click_annotation(self, code: str, on_click: Dict[str, Any]) -> str:
        """替换@OnClick注解为setOnClickListener调用"""
        resource_ids = on_click['ids']
        method_name = on_click['method']
        
        if not resource_ids:
            return code
        
        # 查找@OnClick注解的完整方法
        method_pattern = re.compile(
            rf'@OnClick\s*\(\s*\{\s*((?:R\.id\.\w+(?:\s*,\s*R\.id\.\w+)*)?)\s*\}\s*\)\s*public\s+void\s+{re.escape(method_name)}\s*\([^)]*\)\s*\{[^}]*\}',
            re.MULTILINE | re.DOTALL
        )
        
        # 替换为空的onClick方法（因为事件处理会通过setOnClickListener实现）
        replacement = f"""    public void {method_name}(View view) {{
        // 事件处理逻辑
    }}"""
        
        return method_pattern.sub(replacement, code)
    
    def _add_onclick_listener_initialization(self, code: str, on_clicks: List[Dict[str, Any]]) -> str:
        """添加setOnClickListener初始化代码"""
        if not on_clicks:
            return code
        
        # 生成初始化代码
        initialization_code = self._generate_onclick_initialization_code(on_clicks)
        
        # 尝试在onCreate方法中插入
        code = self._insert_in_oncreate(code, initialization_code)
        
        # 如果没有onCreate方法，尝试在onViewCreated方法中插入
        if not self._has_onclick_initialization_code(code, on_clicks):
            code = self._insert_in_onviewcreated(code, initialization_code)
        
        # 如果还是没有找到合适的方法，在类的末尾添加一个初始化方法
        if not self._has_onclick_initialization_code(code, on_clicks):
            code = self._add_onclick_initialization_method(code, initialization_code)
        
        return code
    
    def _generate_onclick_initialization_code(self, on_clicks: List[Dict[str, Any]]) -> str:
        """生成OnClick初始化代码"""
        lines = []
        
        for on_click in on_clicks:
            resource_ids = on_click['ids']
            method_name = on_click['method']
            
            if not resource_ids:
                continue
            
            # 为每个资源ID生成setOnClickListener调用
            for resource_id in resource_ids:
                # 查找对应的View变量名
                view_name = self._find_view_name_for_resource_id(resource_id)
                
                if view_name:
                    line = f"        {view_name}.setOnClickListener(new View.OnClickListener() {{"
                    lines.append(line)
                    lines.append(f"            @Override")
                    lines.append(f"            public void onClick(View v) {{")
                    lines.append(f"                {method_name}(v);")
                    lines.append(f"            }}")
                    lines.append(f"        }});")
                    lines.append("")
        
        return '\n'.join(lines)
    
    def _find_view_name_for_resource_id(self, resource_id: str) -> str:
        """根据资源ID查找对应的View变量名"""
        # 这里需要从解析的数据中获取，暂时返回一个默认名称
        # 实际实现中应该从parsed_data中获取bind_views信息
        return f"view_{resource_id.split('.')[-1]}"
    
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
                if not self._has_onclick_initialization_code(before_insert, []):
                    return before_insert + '\n' + initialization_code + '\n    ' + after_insert
        
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
                if not self._has_onclick_initialization_code(before_insert, []):
                    return before_insert + '\n' + initialization_code + '\n    ' + after_insert
        
        return code
    
    def _add_onclick_initialization_method(self, code: str, initialization_code: str) -> str:
        """添加OnClick初始化方法"""
        # 查找类的结束位置
        class_end_pattern = re.compile(r'(\s*)\}\s*$', re.MULTILINE)
        
        match = class_end_pattern.search(code)
        if match:
            # 在类结束前添加初始化方法
            method_code = f"""
    private void initializeOnClickListeners() {{
{initialization_code}
    }}
"""
            
            before_end = code[:match.start()]
            after_end = code[match.start():]
            
            return before_end + method_code + after_end
        
        return code
    
    def _has_onclick_initialization_code(self, code: str, on_clicks: List[Dict[str, Any]]) -> bool:
        """检查是否已经包含OnClick初始化代码"""
        if not on_clicks:
            return False
        
        # 检查是否已经有setOnClickListener调用
        for on_click in on_clicks:
            method_name = on_click['method']
            
            pattern = rf'setOnClickListener.*{re.escape(method_name)}'
            if re.search(pattern, code, re.MULTILINE):
                return True
        
        return False
    
    def get_transformation_info(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取转换信息"""
        info = super().get_transformation_info(parsed_data)
        
        if self.can_transform(parsed_data):
            on_clicks = parsed_data.get('on_clicks', [])
            info['changes_count'] = len(on_clicks)
            info['description'] = f"转换 {len(on_clicks)} 个@OnClick注解"
        
        return info
