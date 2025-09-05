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
        
        # 首先移除ButterKnife相关的import语句
        code = self._remove_butterknife_imports(code)
        
        # 检查是否继承自NewBaseActivity或NewBaseFragment（优先级更高）
        if self._is_newbase_activity(code):
            print("DEBUG: 检测到继承自NewBaseActivity或NewBaseFragment，使用定制化处理")
            code = self._inject_for_newbase_activity(code, parsed_data)
        # 检查是否是Holder类
        elif self._is_holder_class(code):
            print("DEBUG: 检测到Holder类，使用Holder特殊处理")
            code = self._inject_for_holder_class(code, parsed_data)
        else:
            # 获取需要注入的代码
            injection_code = self._generate_injection_code(parsed_data)
            
            if injection_code:
                # 只在onCreate方法中注入代码，不创建新方法
                code = self._inject_in_oncreate_only(code, injection_code)
        
        # 处理内部类中的@BindView注解（在所有情况下都要处理）
        code = self._inject_inner_classes(code, parsed_data)
        
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
                            # 如果方法有View参数，传入v（可能需要强转）
                            param_type = on_click.get('param_type', 'View')
                            if param_type == 'View':
                                lines.append(f"        {view_name}.setOnClickListener(v -> {method_name}(v));")
                            else:
                                lines.append(f"        {view_name}.setOnClickListener(v -> {method_name}(({param_type}) v));")
                        else:
                            # 如果方法没有View参数，不传入v
                            lines.append(f"        {view_name}.setOnClickListener(v -> {method_name}());")
                        lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_newbase_injection_code(self, parsed_data: Dict[str, Any]) -> Dict[str, str]:
        """为继承NewBaseActivity的类生成定制化注入代码"""
        bind_views = parsed_data.get('bind_views', [])
        on_clicks = parsed_data.get('on_clicks', [])
        
        # 收集所有需要findViewById的ID
        all_resource_ids = set()
        
        # 从@BindView注解收集ID
        for bind_view in bind_views:
            all_resource_ids.add(bind_view['id'])
        
        # 从@OnClick注解收集ID
        for on_click in on_clicks:
            all_resource_ids.update(on_click['ids'])
        
        # 生成initView方法代码
        init_view_lines = []
        if bind_views:
            init_view_lines.append("        // 初始化View绑定 - 替换@BindView注解")
            
            # 只处理主类中的@BindView注解，过滤掉内部类中的注解
            for bind_view in bind_views:
                field_name = bind_view['name']
                resource_id = bind_view['id']
                
                # 检查这个字段是否属于主类
                if self._is_main_class_field(field_name, bind_views):
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
                        
                        # 检查这个View是否已经在@BindView中声明
                        bind_view_ids = {bind_view['id'] for bind_view in bind_views}
                        
                        if resource_id in bind_view_ids:
                            # 如果View已经在@BindView中声明，直接使用成员变量
                            if has_view_param:
                                param_type = on_click.get('param_type', 'View')
                                if param_type == 'View':
                                    init_listener_lines.append(f"        {view_name}.setOnClickListener(v -> {method_name}(v));")
                                else:
                                    init_listener_lines.append(f"        {view_name}.setOnClickListener(v -> {method_name}(({param_type}) v));")
                            else:
                                init_listener_lines.append(f"        {view_name}.setOnClickListener(v -> {method_name}());")
                        else:
                            # 如果View没有在@BindView中声明，直接在initListener中获取并设置监听器
                            if has_view_param:
                                param_type = on_click.get('param_type', 'View')
                                if param_type == 'View':
                                    init_listener_lines.append(f"        findViewById({resource_id}).setOnClickListener(v -> {method_name}(v));")
                                else:
                                    init_listener_lines.append(f"        findViewById({resource_id}).setOnClickListener(v -> {method_name}(({param_type}) v));")
                            else:
                                init_listener_lines.append(f"        findViewById({resource_id}).setOnClickListener(v -> {method_name}());")
                        init_listener_lines.append("")
        
        return {
            'init_view': '\n'.join(init_view_lines),
            'init_listener': '\n'.join(init_listener_lines)
        }
    
    def _is_newbase_activity(self, code: str) -> bool:
        """检查是否继承自NewBaseActivity或NewBaseFragment（递归检查继承链）"""
        # 首先检查直接继承
        direct_patterns = [
            r'extends\s+NewBaseActivity',
            r'extends\s+\w*NewBaseActivity',
            r'extends\s+NewBaseFragment',
            r'extends\s+\w*NewBaseFragment',
            r'implements\s+.*NewBaseActivity',
            r'implements\s+.*NewBaseFragment'
        ]
        
        for pattern in direct_patterns:
            if re.search(pattern, code, re.MULTILINE):
                return True
        
        # 检查是否有getLayoutId方法（NewBaseActivity的典型特征）
        # 必须是无参数的getLayoutId方法，不是getLayoutId(int viewType)
        if re.search(r'public\s+int\s+getLayoutId\s*\(\s*\)', code, re.MULTILINE):
            return True
        
        # 如果没有直接继承，递归检查继承链
        return self._check_inheritance_chain(code)
    
    def _is_holder_class(self, code: str) -> bool:
        """检查是否是Holder类（继承自BaseHolder）"""
        # 只检查最外层的类（第一个class声明）
        first_class_match = re.search(r'public\s+class\s+(\w+)(?:\s+extends\s+(\w+))?', code)
        if not first_class_match:
            return False
        
        class_name = first_class_match.group(1)
        parent_class = first_class_match.group(2) if first_class_match.group(2) else None
        
        # 检查是否直接继承BaseHolder
        if parent_class and 'BaseHolder' in parent_class:
            return True
        
        # 检查类名是否包含Holder，但排除Activity和Fragment
        if 'Holder' in class_name and 'Activity' not in class_name and 'Fragment' not in class_name:
            return True
        
        return False
    
    def _is_main_class_field(self, field_name: str, bind_views: List[Dict]) -> bool:
        """检查字段是否属于主类（简单启发式方法）"""
        # 明确的Holder字段名
        holder_field_names = [
            'mImgSelected', 'mColorPannelView',  # ColorHolder字段
            'mTvTitle', 'mItemList',             # MyHolder字段  
            'mImgPreview', 'mBtnInstall', 'mFrmPreview',  # WatchThme2ItemHolder字段
            'mTvFileName', 'mCx',                # CashLogDialogFragment.MyHolder字段
            'imgVator', 'tvName', 'tvIds', 'tvSteps',  # FriendsFragment.FriendItemHolder字段
            'tvAddFriendTips', 'btnAgree', 'btnReject', 'tvLabel'  # UserIdeasActivity.MyHolderView字段
        ]
        
        if field_name in holder_field_names:
            return False
        
        # 其他字段默认认为是主类字段
        return True
    
    def _generate_holder_injection_code(self, parsed_data: Dict[str, Any]) -> str:
        """为Holder类生成初始化代码"""
        bind_views = parsed_data.get('bind_views', [])
        on_clicks = parsed_data.get('on_clicks', [])
        
        lines = []
        
        # 生成@BindView的初始化代码
        if bind_views:
            lines.append("        // 初始化View绑定 - 替换@BindView注解")
            for bind_view in bind_views:
                field_name = bind_view['name']
                resource_id = bind_view['id']
                lines.append(f"        {field_name} = itemView.findViewById({resource_id});")
            lines.append("")
        
        # 生成@OnClick的监听器代码
        if on_clicks:
            lines.append("        // 初始化点击事件 - 替换@OnClick注解")
            for on_click in on_clicks:
                method_name = on_click['method']
                resource_ids = on_click['ids']
                has_view_param = on_click.get('has_view_param', True)
                param_type = on_click.get('param_type', 'View')
                
                for resource_id in resource_ids:
                    # 查找对应的View变量名
                    view_name = self._find_view_name_for_resource_id(resource_id, bind_views)
                    
                    if view_name:
                        if has_view_param:
                            if param_type == 'View':
                                lines.append(f"        {view_name}.setOnClickListener(v -> {method_name}(v));")
                            else:
                                lines.append(f"        {view_name}.setOnClickListener(v -> {method_name}(({param_type}) v));")
                        else:
                            lines.append(f"        {view_name}.setOnClickListener(v -> {method_name}());")
                        lines.append("")
        
        return '\n'.join(lines)
    
    def _inject_for_holder_class(self, code: str, parsed_data: Dict[str, Any]) -> str:
        """为Holder类注入初始化代码"""
        # 生成Holder类的初始化代码
        holder_code = self._generate_holder_injection_code(parsed_data)
        
        if not holder_code:
            return code
        
        # 查找构造器方法
        constructor_pattern = re.compile(
            r'public\s+\w+\s*\([^)]*View\s+\w+[^)]*\)\s*\{',
            re.MULTILINE
        )
        
        match = constructor_pattern.search(code)
        if match:
            # 找到构造器，在构造器内部注入代码
            constructor_start = match.end()
            
            # 查找构造器的结束位置
            brace_count = 1
            constructor_end = constructor_start
            
            for i, char in enumerate(code[constructor_start:], constructor_start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        constructor_end = i
                        break
            
            # 在构造器内部注入代码
            before_constructor = code[:constructor_start]
            after_constructor = code[constructor_end:]
            
            # 检查构造器内部是否已经有初始化代码
            constructor_content = code[constructor_start:constructor_end]
            
            # 查找super调用
            super_call_pattern = re.compile(r'super\s*\([^)]*\)\s*;')
            super_match = super_call_pattern.search(constructor_content)
            
            if super_match:
                # 如果有super调用，在super调用后添加初始化代码
                super_end = super_match.end()
                return (before_constructor + 
                       constructor_content[:super_end] + 
                       '\n' + holder_code + 
                       constructor_content[super_end:] + 
                       after_constructor)
            else:
                # 如果没有super调用，直接在构造器开始后添加
                return before_constructor + '\n' + holder_code + constructor_content + after_constructor
        
        return code
    
    def _check_inheritance_chain(self, code: str) -> bool:
        """递归检查继承链中是否包含NewBaseActivity或NewBaseFragment"""
        # 查找当前类的extends声明
        extends_match = re.search(r'class\s+\w+\s+extends\s+(\w+)', code)
        if not extends_match:
            return False
        
        parent_class = extends_match.group(1)
        
        # 如果父类就是NewBaseActivity或NewBaseFragment，直接返回True
        if 'NewBaseActivity' in parent_class or 'NewBaseFragment' in parent_class:
            return True
        
        # 尝试查找父类的定义（在同一个文件中）
        parent_class_pattern = rf'class\s+{re.escape(parent_class)}\s+extends\s+(\w+)'
        parent_extends_match = re.search(parent_class_pattern, code)
        
        if parent_extends_match:
            grandparent_class = parent_extends_match.group(1)
            # 递归检查祖父类
            if 'NewBaseActivity' in grandparent_class or 'NewBaseFragment' in grandparent_class:
                return True
            # 继续递归检查更深层的继承
            return self._check_deeper_inheritance(code, grandparent_class)
        
        # 如果当前文件中没有找到父类定义，检查一些常见的基类模式
        # 这些基类通常继承自NewBaseActivity或NewBaseFragment
        common_base_classes = [
            'BaseActivity', 'BaseFragment', 'TabBaseFragment', 'TabBaseActivity',
            'AppBaseActivity', 'AppBaseFragment', 'CommonBaseActivity', 'CommonBaseFragment',
            'HomeBaseFragment'  # 添加HomeBaseFragment到已知基类列表
        ]
        
        for base_class in common_base_classes:
            if parent_class == base_class:
                # 假设这些基类继承自NewBaseActivity或NewBaseFragment
                return True
        
        return False
    
    def _check_deeper_inheritance(self, code: str, class_name: str) -> bool:
        """检查更深层的继承关系"""
        # 查找指定类的extends声明
        class_pattern = rf'class\s+{re.escape(class_name)}\s+extends\s+(\w+)'
        extends_match = re.search(class_pattern, code)
        
        if not extends_match:
            return False
        
        parent_class = extends_match.group(1)
        
        # 如果找到NewBaseActivity或NewBaseFragment，返回True
        if 'NewBaseActivity' in parent_class or 'NewBaseFragment' in parent_class:
            return True
        
        # 继续递归检查
        return self._check_deeper_inheritance(code, parent_class)
    
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
    
    def _inject_inner_classes(self, code: str, parsed_data: Dict[str, Any]) -> str:
        """处理内部类中的@BindView注解"""
        bind_views = parsed_data.get('bind_views', [])
        
        # 查找所有内部类
        inner_classes = self._find_inner_classes(code)
        
        for inner_class in inner_classes:
            class_name = inner_class['name']
            class_start = inner_class['start']
            class_end = inner_class['end']
            extends = inner_class.get('extends', '')
            
            # 检查是否是Holder类
            if 'Holder' in class_name and 'BaseHolder' in extends:
                # 检查是否已经处理过这个类
                class_content = code[class_start:class_end]
                if '// 初始化View绑定 - 替换@BindView注解' in class_content:
                    continue
                
                # 获取该Holder类特有的字段
                holder_bind_views = self._get_holder_specific_fields(code, class_name, class_start, class_end, bind_views)
                
                if holder_bind_views:
                    holder_code = self._generate_holder_injection_code({'bind_views': holder_bind_views, 'on_clicks': []})
                    
                    # 在Holder类的构造器中注入代码
                    code = self._inject_in_holder_constructor(code, class_start, class_end, holder_code)
        
        return code
    
    def _get_holder_specific_fields(self, code: str, class_name: str, class_start: int, class_end: int, bind_views: List[Dict]) -> List[Dict]:
        """获取特定Holder类中的字段"""
        # 提取该类的代码段
        class_code = code[class_start:class_end]
        
        # 查找该类中声明的字段
        holder_fields = []
        for bind_view in bind_views:
            field_name = bind_view['name']
            field_type = bind_view['type']
            
            # 更精确的字段声明检测：查找 "类型 字段名;" 的模式
            field_declaration_pattern = f"{field_type} {field_name};"
            if field_declaration_pattern in class_code:
                holder_fields.append(bind_view)
        
        return holder_fields
    
    def _find_inner_classes(self, code: str) -> List[Dict]:
        """查找所有内部类"""
        inner_classes = []
        
        # 查找所有class声明
        class_pattern = re.compile(r'class\s+(\w+)(?:\s+extends\s+(\w+))?', re.MULTILINE)
        matches = class_pattern.finditer(code)
        
        for match in matches:
            class_name = match.group(1)
            extends = match.group(2) if match.group(2) else ''
            
            # 跳过最外层的类（查找第一个class声明）
            first_class_match = re.search(r'public\s+class\s+\w+', code)
            if first_class_match and match.start() <= first_class_match.end():
                continue
            
            # 查找类的结束位置
            brace_count = 0
            class_end = match.end()
            in_class = False
            
            for i, char in enumerate(code[match.end():], match.end()):
                if char == '{':
                    brace_count += 1
                    in_class = True
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0 and in_class:
                        class_end = i + 1
                        break
            
            inner_classes.append({
                'name': class_name,
                'extends': extends,
                'start': match.start(),
                'end': class_end
            })
        
        return inner_classes
    
    def _inject_in_holder_constructor(self, code: str, class_start: int, class_end: int, holder_code: str) -> str:
        """在Holder类的构造器中注入代码"""
        class_content = code[class_start:class_end]
        
        # 检查是否已经注入了代码
        if '// 初始化View绑定 - 替换@BindView注解' in class_content:
            return code
        
        # 查找构造器
        constructor_pattern = re.compile(r'public\s+\w+\s*\([^)]*View\s+\w+[^)]*\)\s*\{', re.MULTILINE)
        constructor_match = constructor_pattern.search(class_content)
        
        if constructor_match:
            constructor_start = class_start + constructor_match.end()
            
            # 查找构造器的结束位置
            brace_count = 1
            constructor_end = constructor_start
            
            for i, char in enumerate(code[constructor_start:], constructor_start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        constructor_end = i
                        break
            
            # 在构造器内部注入代码
            before_constructor = code[:constructor_start]
            after_constructor = code[constructor_end:]
            
            # 查找super调用
            constructor_content = code[constructor_start:constructor_end]
            super_call_pattern = re.compile(r'super\s*\([^)]*\)\s*;')
            super_match = super_call_pattern.search(constructor_content)
            
            if super_match:
                super_end = constructor_start + super_match.end()
                return (before_constructor + 
                       constructor_content[:super_match.end()] + 
                       '\n' + holder_code + 
                       constructor_content[super_match.end():] + 
                       after_constructor)
            else:
                return before_constructor + '\n' + holder_code + constructor_content + after_constructor
        
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
        super.initViews();
{init_view_code}
    }}"""
        
        # 在类的结束位置前插入方法
        class_end_pos = self._find_class_end_position(code)
        if class_end_pos != -1:
            # 在类的结束大括号之前插入方法
            before_end = code[:class_end_pos-1]  # 减去1，在结束大括号之前插入
            after_end = code[class_end_pos-1:]   # 从结束大括号开始
            return before_end + method_code + "\n" + after_end
        
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
            # 在类的结束大括号之前插入方法
            before_end = code[:class_end_pos-1]  # 减去1，在结束大括号之前插入
            after_end = code[class_end_pos-1:]   # 从结束大括号开始
            return before_end + method_code + "\n" + after_end
        
        return code
    
    def _update_init_view_method(self, code: str, init_view_code: str) -> str:
        """更新现有的initViews方法"""
        # 使用更精确的方法来找到initViews方法的结束位置
        lines = code.split('\n')
        method_start_line = -1
        method_end_line = -1
        
        # 找到initViews方法的开始行
        for i, line in enumerate(lines):
            if 'protected void initViews() {' in line or 'public void initViews() {' in line:
                method_start_line = i
                break
        
        if method_start_line == -1:
            return code
        
        # 找到initViews方法的结束行（正确处理嵌套大括号）
        brace_count = 0
        for i in range(method_start_line, len(lines)):
            line = lines[i]
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0 and i > method_start_line:
                method_end_line = i
                break
        
        if method_end_line == -1:
            return code
        
        # 提取原有方法内容
        original_lines = lines[method_start_line + 1:method_end_line]
        original_content = '\n'.join(original_lines)
        
        # 检查是否已经有super.initViews()调用
        has_super_call = 'super.initViews()' in original_content
        
        # 构建新的方法内容
        if has_super_call:
            new_content = '        super.initViews();\n' + init_view_code
        else:
            new_content = '        super.initViews();\n' + init_view_code
        
        # 替换方法内容
        new_lines = lines[:method_start_line + 1] + [new_content] + lines[method_end_line:]
        return '\n'.join(new_lines)
    
    def _update_init_listener_method(self, code: str, init_listener_code: str) -> str:
        """更新现有的initListener方法"""
        # 使用更精确的方法来找到initListener方法的结束位置
        lines = code.split('\n')
        method_start_line = -1
        method_end_line = -1
        
        # 找到initListener方法的开始行
        for i, line in enumerate(lines):
            if 'public void initListener() {' in line or 'protected void initListener() {' in line:
                method_start_line = i
                break
        
        if method_start_line == -1:
            return code
        
        # 找到initListener方法的结束行（正确处理嵌套大括号）
        brace_count = 0
        for i in range(method_start_line, len(lines)):
            line = lines[i]
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0 and i > method_start_line:
                method_end_line = i
                break
        
        if method_end_line == -1:
            return code
        
        # 提取原有方法内容
        original_lines = lines[method_start_line + 1:method_end_line]
        original_content = '\n'.join(original_lines)
        
        # 构建新的方法内容
        if original_content.strip():
            # 如果原有内容不为空，在末尾追加
            new_content = original_content + '\n        \n        // 新增的点击事件监听器\n' + init_listener_code
        else:
            # 如果原有内容为空，直接添加新内容
            new_content = '\n' + init_listener_code
        
        # 替换方法内容
        new_lines = lines[:method_start_line + 1] + [new_content] + lines[method_end_line:]
        return '\n'.join(new_lines)
    
    def _find_class_end_position(self, code: str) -> int:
        """找到类的真正结束位置（最后一个大括号）"""
        # 使用更精确的方法：找到最外层类的结束大括号
        brace_count = 0
        in_string = False
        string_char = None
        in_comment = False
        class_started = False
        
        for i, char in enumerate(code):
            # 处理注释
            if not in_string and not in_comment:
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
            
            if in_string or in_comment:
                continue
            
            if char == '{':
                if not class_started:
                    # 找到第一个开括号，说明类开始了
                    class_started = True
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if class_started and brace_count == 0:
                    # 找到匹配的闭括号，这是类的结束位置
                    return i + 1
        
        return -1
    
    def _find_view_name_for_resource_id(self, resource_id: str, bind_views: List[Dict[str, Any]]) -> Optional[str]:
        """根据资源ID查找对应的View变量名"""
        # 首先从@BindView注解中查找
        for bind_view in bind_views:
            if bind_view['id'] == resource_id:
                return bind_view['name']
        
        # 如果没找到，生成一个通用的View变量名
        return self._generate_view_name_from_id(resource_id)
    
    def _generate_view_name_from_id(self, resource_id: str) -> str:
        """根据资源ID生成View变量名"""
        # 从资源ID中提取名称部分，例如 R.id.submit_button -> submit_button
        if '.' in resource_id:
            id_name = resource_id.split('.')[-1]
            # 转换为驼峰命名法
            view_name = f"view_{id_name}"
            return view_name
        
        # 如果格式不符合预期，使用默认名称
        return f"view_{resource_id.replace('.', '_').replace('R_id_', '')}"
    
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
    
    def _remove_butterknife_imports(self, code: str) -> str:
        """移除ButterKnife相关的import语句"""
        lines = code.split('\n')
        filtered_lines = []
        
        for line in lines:
            # 检查是否是ButterKnife相关的import语句
            if (line.strip().startswith('import') and 
                ('butterknife' in line.lower() or 
                 'BindView' in line or 
                 'OnClick' in line or
                 'BindString' in line or
                 'BindColor' in line or
                 'BindDimen' in line or
                 'BindDrawable' in line or
                 'BindBitmap' in line or
                 'BindInt' in line or
                 'BindFloat' in line or
                 'BindBoolean' in line or
                 'BindArray' in line or
                 'BindFont' in line or
                 'BindAnim' in line or
                 'BindAnimator' in line or
                 'BindBool' in line or
                 'BindDimen' in line or
                 'BindDrawable' in line or
                 'BindInt' in line or
                 'BindString' in line)):
                print(f"DEBUG: 移除ButterKnife import语句: {line.strip()}")
                continue
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
