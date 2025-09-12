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
        
        # 替换@OnClick注解为普通方法
        for on_click in on_clicks:
            transformed_code = self._replace_on_click_annotation(
                transformed_code, on_click
            )
        
        # 添加setOnClickListener初始化代码
        transformed_code = self._add_onclick_listener_initialization(transformed_code, on_clicks)
        
        return transformed_code
    
    def _replace_on_click_annotation(self, code: str, on_click: Dict[str, Any]) -> str:
        """替换@OnClick注解为普通方法"""
        resource_ids = on_click['ids']
        method_name = on_click['method']
        
        if not resource_ids:
            return code
        
        # 使用更简单的正则表达式，匹配所有@OnClick注解
        # 包括单参数和多参数的情况
        annotation_pattern = re.compile(
            r'@OnClick\s*\(\s*(?:\{\s*)?(?:R\.id\.\w+(?:\s*,\s*R\.id\.\w+)*)?(?:\s*\})?\s*\)',
            re.MULTILINE
        )
        
        # 只移除注解，保留方法定义
        return annotation_pattern.sub('', code)
    
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
                if not self._has_onclick_initialization_code(before_insert, []):
                    return before_insert + '\n' + initialization_code + '\n    ' + after_insert
        
        return code
    
    def _add_onclick_initialization_method(self, code: str, initialization_code: str) -> str:
        """添加OnClick初始化方法"""
        # 查找主类的结束位置（排除内部类）
        main_class_end = self._find_main_class_end(code)
        
        if main_class_end != -1:
            # 在类结束前添加初始化方法
            method_code = f"""
    private void initListener() {{
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
    
    def _has_onclick_initialization_code(self, code: str, on_clicks: List[Dict[str, Any]]) -> bool:
        """检查是否已经包含OnClick初始化代码"""
        if not on_clicks:
            return False
        
        # 检查是否已经有setOnClickListener调用
        for on_click in on_clicks:
            method_name = on_click['method']
            
            escaped_method_name = re.escape(method_name)
            pattern = r'setOnClickListener.*' + escaped_method_name
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
