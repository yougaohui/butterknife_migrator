#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码注入器
将初始化语句插入到 onCreate() 或 onViewCreated() 方法体中
支持定位方法块、插入语句、避免重复
"""

import re
from typing import Dict, Any, List, Optional, Tuple


class CodeInjector:
    """代码注入器类"""
    
    def __init__(self):
        # 编译正则表达式
        self.onCreate_pattern = re.compile(
            r'(\s*@Override\s*\n?\s*protected\s+void\s+onCreate\s*\([^)]*\)\s*\{)',
            re.MULTILINE
        )
        
        self.onViewCreated_pattern = re.compile(
            r'(\s*@Override\s*\n\s*public\s+void\s+onViewCreated\s*\([^)]*\)\s*\{)',
            re.MULTILINE
        )
        
        self.method_body_pattern = re.compile(
            r'(\s*@Override\s*\n\s*(?:public|private|protected)\s+(?:static\s+)?\w+\s+\w+\s*\([^)]*\)\s*\{)',
            re.MULTILINE
        )
        
        self.class_end_pattern = re.compile(
            r'(\s*)\}\s*$',
            re.MULTILINE
        )
    
    def inject(self, code: str, parsed_data: Dict[str, Any]) -> str:
        """注入初始化代码"""
        if not parsed_data.get('has_butterknife', False):
            return code
        
        # 检查是否继承自NewBaseActivity或NewBaseFragment
        if self._is_newbase_activity(code):
            print("DEBUG: 检测到继承自NewBaseActivity或NewBaseFragment，使用定制化处理")
            return self._inject_for_newbase_activity(code, parsed_data)
        
        # 获取需要注入的代码
        injection_code = self._generate_injection_code(parsed_data)
        
        if not injection_code:
            return code
        
        # 只在onCreate方法中注入代码，不创建新方法
        code = self._inject_in_oncreate_only(code, injection_code)
        
        return code
    
    def _generate_injection_code(self, parsed_data: Dict[str, Any]) -> str:
        """生成需要注入的代码"""
        lines = []
        
        # 1. 首先处理@BindView注解，生成findViewById初始化代码
        bind_views = parsed_data.get('bind_views', [])
        if bind_views:
            lines.append("        // 初始化View绑定 - 替换@BindView注解")
            for bind_view in bind_views:
                field_name = bind_view['name']
                resource_id = bind_view['id']
                field_type = bind_view['type']
                
                # 生成findViewById调用，确保在移除@BindView注解前先赋值
                line = f"        {field_name} = findViewById({resource_id});"
                lines.append(line)
            lines.append("")
        
        # 2. 处理@OnClick注解，生成setOnClickListener初始化代码
        # 保留@OnClick注解下的完整方法，只移除注解本身，然后为每个View设置监听器
        on_clicks = parsed_data.get('on_clicks', [])
        if on_clicks:
            lines.append("        // 初始化点击事件 - 替换@OnClick注解")
            for on_click in on_clicks:
                resource_ids = on_click['ids']
                method_name = on_click['method']
                
                for resource_id in resource_ids:
                    # 查找对应的View变量名
                    view_name = self._find_view_name_for_resource_id(resource_id, bind_views)
                    
                    if view_name:
                        # 检查方法是否有View参数
                        has_view_param = on_click.get('has_view_param', True)  # 默认为True保持向后兼容
                        
                        # 生成setOnClickListener调用，使用Lambda表达式
                        if has_view_param:
                            # 如果方法有View参数，传入v
                            lines.append(f"        {view_name}.setOnClickListener(v -> {method_name}(v));")
                        else:
                            # 如果方法没有View参数，不传入v
                            lines.append(f"        {view_name}.setOnClickListener(v -> {method_name}());")
                        lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_newbase_injection_code(self, parsed_data: Dict[str, Any]) -> Dict[str, str]:
        """为继承NewBaseActivity的类生成定制化注入代码"""
        bind_views = parsed_data.get('bind_views', [])
        on_clicks = parsed_data.get('on_clicks', [])
        
        # 生成initView方法代码
        init_view_lines = []
        if bind_views:
            init_view_lines.append("        // 初始化View绑定 - 替换@BindView注解")
            for bind_view in bind_views:
                field_name = bind_view['name']
                resource_id = bind_view['id']
                field_type = bind_view['type']
                
                line = f"        {field_name} = findViewById({resource_id});"
                init_view_lines.append(line)
        
        # 生成initListener方法代码
        init_listener_lines = []
        if on_clicks:
            init_listener_lines.append("        // 初始化点击事件 - 替换@OnClick注解")
            for on_click in on_clicks:
                resource_ids = on_click['ids']
                method_name = on_click['method']
                
                for resource_id in resource_ids:
                    # 查找对应的View变量名
                    view_name = self._find_view_name_for_resource_id(resource_id, bind_views)
                    
                    if view_name:
                        # 检查方法是否有View参数
                        has_view_param = on_click.get('has_view_param', True)  # 默认为True保持向后兼容
                        
                        # 生成setOnClickListener调用，使用Lambda表达式
                        if has_view_param:
                            # 如果方法有View参数，传入v
                            init_listener_lines.append(f"        {view_name}.setOnClickListener(v -> {method_name}(v));")
                        else:
                            # 如果方法没有View参数，不传入v
                            init_listener_lines.append(f"        {view_name}.setOnClickListener(v -> {method_name}());")
                        init_listener_lines.append("")
        
        return {
            'init_view': '\n'.join(init_view_lines),
            'init_listener': '\n'.join(init_listener_lines)
        }
    
    def _is_newbase_activity(self, code: str) -> bool:
        """检查是否继承自NewBaseActivity或NewBaseFragment"""
        newbase_patterns = [
            r'extends\s+NewBaseActivity',
            r'extends\s+\w*NewBaseActivity',
            r'extends\s+NewBaseFragment',
            r'extends\s+\w*NewBaseFragment',
            r'implements\s+.*NewBaseActivity',
            r'implements\s+.*NewBaseFragment'
        ]
        
        for pattern in newbase_patterns:
            if re.search(pattern, code, re.MULTILINE):
                return True
        
        return False
    
    def _inject_for_newbase_activity(self, code: str, parsed_data: Dict[str, Any]) -> str:
        """为继承NewBaseActivity或NewBaseFragment的类进行定制化注入"""
        # 生成定制化注入代码
        injection_codes = self._generate_newbase_injection_code(parsed_data)
        
        # 检查方法是否已存在，如果存在则更新，否则创建
        if injection_codes['init_view']:
            if self._has_init_view_method(code):
                print("DEBUG: initView方法已存在，更新其内容")
                code = self._update_init_view_method(code, injection_codes['init_view'])
            else:
                print("DEBUG: 创建新的initView方法")
                code = self._create_init_view_method(code, injection_codes['init_view'])
        
        if injection_codes['init_listener']:
            if self._has_init_listener_method(code):
                print("DEBUG: initListener方法已存在，更新其内容")
                code = self._update_init_listener_method(code, injection_codes['init_listener'])
            else:
                print("DEBUG: 创建新的initListener方法")
                code = self._create_init_listener_method(code, injection_codes['init_listener'])
        
        return code
    
    def _has_init_view_method(self, code: str) -> bool:
        """检查是否已存在initViews方法"""
        return 'protected void initViews()' in code or 'public void initViews()' in code
    
    def _has_init_listener_method(self, code: str) -> bool:
        """检查是否已存在initListener方法"""
        return 'public void initListener()' in code or 'protected void initListener()' in code
    
    def _create_init_view_method(self, code: str, init_view_code: str) -> str:
        """创建initViews方法"""
        method_code = f"""
    @Override
    protected void initViews() {{
{init_view_code}
    }}"""
        
        # 在类的结束位置前插入方法
        class_end_pos = self._find_class_end_position(code)
        if class_end_pos != -1:
            before_end = code[:class_end_pos]
            after_end = code[class_end_pos:]
            return before_end + method_code + after_end
        
        return code
    
    def _create_init_listener_method(self, code: str, init_listener_code: str) -> str:
        """创建initListener方法"""
        method_code = f"""
    @Override
    public void initListener() {{
{init_listener_code}
    }}"""
        
        # 在类的结束位置前插入方法
        class_end_pos = self._find_class_end_position(code)
        if class_end_pos != -1:
            before_end = code[:class_end_pos]
            after_end = code[class_end_pos:]
            return before_end + method_code + after_end
        
        return code
    
    def _update_init_view_method(self, code: str, init_view_code: str) -> str:
        """更新现有的initViews方法"""
        # 查找initViews方法并替换其内容
        pattern = re.compile(
            r'(@Override\s*\n\s*(?:public|protected)\s+void\s+initViews\s*\(\s*\)\s*\{)([^}]*)(\})',
            re.MULTILINE | re.DOTALL
        )
        
        def replace_method(match):
            method_start = match.group(1)
            method_end = match.group(3)
            return method_start + '\n' + init_view_code + '\n    ' + method_end
        
        return pattern.sub(replace_method, code)
    
    def _update_init_listener_method(self, code: str, init_listener_code: str) -> str:
        """更新现有的initListener方法"""
        # 查找initListener方法并追加新的监听器代码
        pattern = re.compile(
            r'(@Override\s*\n\s*(?:public|protected)\s+void\s+initListener\s*\(\s*\)\s*\{)([^}]*)(\})',
            re.MULTILINE | re.DOTALL
        )
        
        def replace_method(match):
            method_start = match.group(1)
            original_content = match.group(2)
            method_end = match.group(3)
            
            # 保留原有内容，并在末尾追加新的监听器代码
            if original_content.strip():
                # 如果原有内容不为空，在末尾追加
                return method_start + original_content + '\n        \n        // 新增的点击事件监听器\n' + init_listener_code + '\n    ' + method_end
            else:
                # 如果原有内容为空，直接添加新内容
                return method_start + '\n' + init_listener_code + '\n    ' + method_end
        
        return pattern.sub(replace_method, code)
    
    def _find_class_end_position(self, code: str) -> int:
        """找到类的真正结束位置（最后一个大括号）"""
        # 使用更简单的方法：找到最后一个独立的 '}'
        lines = code.split('\n')
        
        # 从后往前查找最后一个大括号
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if line == '}':
                # 找到最后一个大括号，计算其在原代码中的位置
                pos = 0
                for j in range(i):
                    pos += len(lines[j]) + 1  # +1 for newline
                return pos
        
        return -1
    
    def _find_view_name_for_resource_id(self, resource_id: str, bind_views: List[Dict[str, Any]]) -> Optional[str]:
        """根据资源ID查找对应的View变量名"""
        for bind_view in bind_views:
            if bind_view['id'] == resource_id:
                return bind_view['name']
        
        # 如果没有找到，返回一个默认名称
        return f"view_{resource_id.split('.')[-1]}"
    
    def _inject_in_existing_methods(self, code: str, injection_code: str) -> str:
        """在现有方法中注入代码"""
        # 1. 尝试在onCreate方法中注入
        code = self._inject_in_method(code, injection_code, self.onCreate_pattern, "onCreate")
        
        # 2. 尝试在onViewCreated方法中注入
        if not self._has_injection_code(code, injection_code):
            code = self._inject_in_method(code, injection_code, self.onViewCreated_pattern, "onViewCreated")
        
        # 3. 尝试在其他合适的方法中注入
        if not self._has_injection_code(code, injection_code):
            code = self._inject_in_any_method(code, injection_code)
        
        return code
    
    def _inject_in_method(self, code: str, injection_code: str, pattern: re.Pattern, method_name: str) -> str:
        """在指定方法中注入代码"""
        match = pattern.search(code)
        if not match:
            return code
        
        # 找到方法开始位置
        method_start = match.end()
        
        # 查找方法体结束位置
        method_end = self._find_method_end(code, method_start)
        
        if method_end > method_start:
            # 在方法体结束前插入代码
            before_end = code[:method_end]
            after_end = code[method_end:]
            
            # 检查是否已经有注入的代码
            if not self._has_injection_code(before_end, injection_code):
                return before_end + '\n' + injection_code + '\n    ' + after_end
        
        return code
    
    def _inject_in_any_method(self, code: str, injection_code: str) -> str:
        """在任何合适的方法中注入代码"""
        # 查找所有方法
        methods = list(self.method_body_pattern.finditer(code))
        
        for method in methods:
            method_start = method.end()
            method_end = self._find_method_end(code, method_start)
            
            if method_end > method_start:
                # 检查方法是否合适（不是getter/setter等）
                method_content = code[method_start:method_end]
                if self._is_suitable_method_for_injection(method_content):
                    # 在方法体结束前插入代码
                    before_end = code[:method_end]
                    after_end = code[method_end:]
                    
                    # 检查是否已经有注入的代码
                    if not self._has_injection_code(before_end, injection_code):
                        return before_end + '\n' + injection_code + '\n    ' + after_end
        
        return code
    
    def _find_method_end(self, code: str, start_pos: int) -> int:
        """查找方法体结束位置"""
        brace_count = 0
        in_string = False
        string_char = None
        
        for i, char in enumerate(code[start_pos:], start_pos):
            # 处理字符串字面量
            if char == '"' or char == "'":
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
                continue
            
            if in_string:
                continue
            
            # 处理大括号
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    return i + 1
        
        # 如果没有找到匹配的结束大括号，返回代码末尾
        return len(code)
    
    def _find_oncreate_method_end(self, code: str, start_pos: int) -> int:
        """专门查找onCreate方法的结束位置，使用更精确的算法"""
        brace_count = 0
        in_string = False
        string_char = None
        
        for i, char in enumerate(code[start_pos:], start_pos):
            # 处理字符串字面量
            if char == '"' or char == "'":
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
                continue
            
            if in_string:
                continue
            
            # 处理大括号
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    # 找到onCreate方法结束位置
                    return i + 1
                elif brace_count < 0:
                    # 如果大括号计数变为负数，说明已经超出了方法边界
                    # 这种情况不应该发生，但为了安全起见，返回当前位置
                    return i
        
        # 如果没有找到匹配的结束大括号，返回代码末尾
        return len(code)
    
    def _is_suitable_method_for_injection(self, method_content: str) -> bool:
        """检查方法是否适合注入初始化代码"""
        # 排除getter/setter方法
        if re.search(r'get[A-Z]|set[A-Z]', method_content):
            return False
        
        # 排除构造函数
        if re.search(r'public\s+\w+\s*\(', method_content):
            return False
        
        # 排除私有方法
        if re.search(r'private\s+\w+\s+\w+\s*\(', method_content):
            return False
        
        return True
    
    def _create_initialization_method(self, code: str, injection_code: str) -> str:
        """创建新的初始化方法"""
        # 查找类的结束位置
        match = self.class_end_pattern.search(code)
        if not match:
            return code
        
        # 在类结束前添加初始化方法
        method_code = f"""
    private void initializeViews() {{
{injection_code}
    }}
"""
        
        before_end = code[:match.start()]
        after_end = code[match.start():]
        
        return before_end + method_code + after_end
    
    def _has_injection_code(self, code: str, injection_code: str) -> bool:
        """检查是否已经包含注入的代码"""
        if not injection_code:
            return True
        
        # 检查关键代码片段是否已经存在
        key_lines = []
        for line in injection_code.split('\n'):
            line = line.strip()
            if line and not line.startswith('//'):
                key_lines.append(line)
        
        for key_line in key_lines:
            if key_line not in code:
                return False
        
        return True
    
    def _inject_in_oncreate_only(self, code: str, injection_code: str) -> str:
        """只在onCreate方法中注入代码，不创建新方法"""
        print(f"DEBUG: 尝试在onCreate方法中注入代码")
        print(f"DEBUG: 注入代码长度: {len(injection_code)}")
        
        match = self.onCreate_pattern.search(code)
        if not match:
            print(f"DEBUG: 没有找到onCreate方法")
            return code
        
        print(f"DEBUG: 找到onCreate方法，位置: {match.start()}-{match.end()}")
        print(f"DEBUG: onCreate方法内容: {repr(match.group(0))}")
        
        method_start = match.end()
        
        # 查找setContentView之后的位置，在那里注入代码
        setcontentview_pattern = re.compile(r'setContentView\s*\([^)]*\)\s*;', re.MULTILINE)
        setcontentview_match = setcontentview_pattern.search(code, method_start)
        
        if setcontentview_match:
            # 在setContentView之后注入代码
            injection_position = setcontentview_match.end()
            print(f"DEBUG: 在setContentView之后注入代码，位置: {injection_position}")
            
            before_injection = code[:injection_position]
            after_injection = code[injection_position:]
            
            if not self._has_injection_code(before_injection, injection_code):
                print(f"DEBUG: 注入代码到setContentView之后")
                result = before_injection + '\n' + injection_code + '\n' + after_injection
                print(f"DEBUG: 注入后的代码长度: {len(result)}")
                return result
            else:
                print(f"DEBUG: 代码已经存在，跳过注入")
        else:
            # 如果没有找到setContentView，在onCreate方法末尾注入
            method_end = self._find_oncreate_method_end(code, method_start)
            print(f"DEBUG: 没有找到setContentView，在onCreate方法末尾注入，位置: {method_end}")
            
            if method_end > method_start:
                before_end = code[:method_end]
                after_end = code[method_end:]
                
                if not self._has_injection_code(before_end, injection_code):
                    print(f"DEBUG: 注入代码到onCreate方法末尾")
                    result = before_end + '\n' + injection_code + '\n    ' + after_end
                    print(f"DEBUG: 注入后的代码长度: {len(result)}")
                    return result
                else:
                    print(f"DEBUG: 代码已经存在，跳过注入")
        
        return code
    
    def get_injection_info(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取注入信息"""
        info = {
            'has_butterknife': parsed_data.get('has_butterknife', False),
            'bind_views_count': len(parsed_data.get('bind_views', [])),
            'on_clicks_count': len(parsed_data.get('on_clicks', [])),
            'injection_methods': []
        }
        
        if info['has_butterknife']:
            if info['bind_views_count'] > 0:
                info['injection_methods'].append('findViewById初始化')
            
            if info['on_clicks_count'] > 0:
                info['injection_methods'].append('OnClickListener设置')
        
        return info
