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
        
        # 检查是否是Holder类（优先级最高）
        if self._is_holder_class(code):
            print("DEBUG: 检测到Holder类，使用Holder特殊处理")
            code = self._inject_for_holder_class(code, parsed_data)
        # 检查是否有setContentView（优先级第二，即使继承BaseActivity也要按通用原则处理）
        elif self._has_setcontentview(code):
            print("DEBUG: 检测到有setContentView，使用通用迁移处理")
            code = self._inject_for_general_activity(code, parsed_data)
        # 检查是否继承自NewBaseActivity或NewBaseFragment（但没有setContentView）
        elif self._is_newbase_activity(code):
            print("DEBUG: 检测到继承自NewBaseActivity或NewBaseFragment，使用定制化处理")
            code = self._inject_for_newbase_activity(code, parsed_data)
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
                # 将R2.id转换为R.id
                if resource_id.startswith('R2.id.'):
                    resource_id = resource_id.replace('R2.id.', 'R.id.')
                line = f"        {field_name} = findViewById({resource_id});"
                lines.append(line)
            lines.append("")
        
        # 2. 处理@OnClick注解，生成setOnClickListener初始化代码
        # 直接使用findViewById调用，不查找View变量名
        on_clicks = parsed_data.get('on_clicks', [])
        if on_clicks:
            lines.append("        // 初始化点击事件 - 替换@OnClick注解")
            for on_click in on_clicks:
                resource_ids = on_click['ids']
                method_name = on_click['method']
                
                for resource_id in resource_ids:
                    # 将R2.id转换为R.id
                    if resource_id.startswith('R2.id.'):
                        resource_id = resource_id.replace('R2.id.', 'R.id.')
                    
                    # 检查方法是否有View参数
                    has_view_param = on_click.get('has_view_param', True)  # 默认为True保持向后兼容
                    
                    # 生成setOnClickListener调用，直接使用findViewById
                    if has_view_param:
                        # 如果方法有View参数，传入v
                        lines.append(f"        findViewById({resource_id}).setOnClickListener(v -> {method_name}(v));")
                    else:
                        # 如果方法没有View参数，不传入v
                        lines.append(f"        findViewById({resource_id}).setOnClickListener(v -> {method_name}());")
        
        # 处理@OnLongClick注解
        on_long_clicks = parsed_data.get('on_long_clicks', [])
        if on_long_clicks:
            lines.append("        // 初始化长按事件 - 替换@OnLongClick注解")
            for on_long_click in on_long_clicks:
                resource_ids = on_long_click['ids']
                method_name = on_long_click['method']
                
                for resource_id in resource_ids:
                    # 查找对应的View变量名
                    view_name = self._find_view_name_for_resource_id(resource_id, bind_views)
                    
                    if view_name:
                        # 检查方法是否有View参数
                        has_view_param = on_long_click.get('has_view_param', True)  # 默认为True保持向后兼容
                        
                        # 生成setOnLongClickListener调用，使用Lambda表达式
                        if has_view_param:
                            # 如果方法有View参数，传入v（可能需要强转）
                            param_type = on_long_click.get('param_type', 'View')
                            if param_type == 'View':
                                lines.append(f"        {view_name}.setOnLongClickListener(v -> {method_name}(v));")
                            else:
                                lines.append(f"        {view_name}.setOnLongClickListener(v -> {method_name}(({param_type}) v));")
                        else:
                            # 如果方法没有View参数，不传入v，但需要返回boolean值
                            lines.append(f"        {view_name}.setOnLongClickListener(v -> {method_name}());")
                        lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_newbase_injection_code(self, parsed_data: Dict[str, Any]) -> Dict[str, str]:
        """为继承NewBaseActivity的类生成定制化注入代码"""
        bind_views = parsed_data.get('bind_views', [])
        on_clicks = parsed_data.get('on_clicks', [])
        on_long_clicks = parsed_data.get('on_long_clicks', [])
        
        # 收集所有需要findViewById的ID
        all_resource_ids = set()
        
        # 从@BindView注解收集ID
        for bind_view in bind_views:
            all_resource_ids.add(bind_view['id'])
        
        # 从@OnClick注解收集ID
        for on_click in on_clicks:
            all_resource_ids.update(on_click['ids'])
        
        # 从@OnLongClick注解收集ID
        for on_long_click in on_long_clicks:
            all_resource_ids.update(on_long_click['ids'])
        
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
                    # 将R2.id转换为R.id
                    if resource_id.startswith('R2.id.'):
                        resource_id = resource_id.replace('R2.id.', 'R.id.')
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
                        
                        # 对于普通Activity，统一使用findViewById，不使用成员变量
                        # 将R2.id转换为R.id
                        if resource_id.startswith('R2.id.'):
                            resource_id = resource_id.replace('R2.id.', 'R.id.')
                        if has_view_param:
                            param_type = on_click.get('param_type', 'View')
                            if param_type == 'View':
                                init_listener_lines.append(f"        findViewById({resource_id}).setOnClickListener(v -> {method_name}(v));")
                            else:
                                init_listener_lines.append(f"        findViewById({resource_id}).setOnClickListener(v -> {method_name}(({param_type}) v));")
                        else:
                            init_listener_lines.append(f"        findViewById({resource_id}).setOnClickListener(v -> {method_name}());")
                        init_listener_lines.append("")
        
        if on_long_clicks:
            init_listener_lines.append("        // 初始化长按事件 - 替换@OnLongClick注解")
            for on_long_click in on_long_clicks:
                resource_ids = on_long_click['ids']
                method_name = on_long_click['method']
                
                for resource_id in resource_ids:
                    # 查找对应的View变量名
                    view_name = self._find_view_name_for_resource_id(resource_id, bind_views)
                    
                    if view_name:
                        # 检查方法是否有View参数
                        has_view_param = on_long_click.get('has_view_param', True)  # 默认为True保持向后兼容
                        
                        # 对于普通Activity，统一使用findViewById，不使用成员变量
                        # 将R2.id转换为R.id
                        if resource_id.startswith('R2.id.'):
                            resource_id = resource_id.replace('R2.id.', 'R.id.')
                        if has_view_param:
                            param_type = on_long_click.get('param_type', 'View')
                            if param_type == 'View':
                                init_listener_lines.append(f"        findViewById({resource_id}).setOnLongClickListener(v -> {method_name}(v));")
                            else:
                                init_listener_lines.append(f"        findViewById({resource_id}).setOnLongClickListener(v -> {method_name}(({param_type}) v));")
                        else:
                            init_listener_lines.append(f"        findViewById({resource_id}).setOnLongClickListener(v -> {method_name}());")
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
        """检查是否是Holder类（继承自BaseHolder或RecyclerView.ViewHolder）"""
        # 只检查最外层的类（第一个class声明）
        first_class_match = re.search(r'public\s+class\s+(\w+)(?:\s+extends\s+([^\{]+))?', code)
        if not first_class_match:
            return False
        
        class_name = first_class_match.group(1)
        parent_class = first_class_match.group(2) if first_class_match.group(2) else None
        
        # 检查是否继承BaseHolder
        if parent_class and 'BaseHolder' in parent_class:
            return True
        
        # 检查是否继承RecyclerView.ViewHolder
        if parent_class and 'RecyclerView.ViewHolder' in parent_class:
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
                # 将R2.id转换为R.id
                if resource_id.startswith('R2.id.'):
                    resource_id = resource_id.replace('R2.id.', 'R.id.')
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
                    else:
                        # 如果View没有在@BindView中声明，直接在构造器中获取并设置监听器
                        # 将R2.id转换为R.id
                        if resource_id.startswith('R2.id.'):
                            resource_id = resource_id.replace('R2.id.', 'R.id.')
                        if has_view_param:
                            if param_type == 'View':
                                lines.append(f"        itemView.findViewById({resource_id}).setOnClickListener(v -> {method_name}(v));")
                            else:
                                lines.append(f"        itemView.findViewById({resource_id}).setOnClickListener(v -> {method_name}(({param_type}) v));")
                        else:
                            lines.append(f"        itemView.findViewById({resource_id}).setOnClickListener(v -> {method_name}());")
                lines.append("")
        
        # 生成@OnLongClick的监听器代码
        on_long_clicks = parsed_data.get('on_long_clicks', [])
        if on_long_clicks:
            lines.append("        // 初始化长按事件 - 替换@OnLongClick注解")
            for on_long_click in on_long_clicks:
                method_name = on_long_click['method']
                resource_ids = on_long_click['ids']
                has_view_param = on_long_click.get('has_view_param', True)
                param_type = on_long_click.get('param_type', 'View')
                
                for resource_id in resource_ids:
                    # 查找对应的View变量名
                    view_name = self._find_view_name_for_resource_id(resource_id, bind_views)
                    
                    if view_name:
                        if has_view_param:
                            if param_type == 'View':
                                lines.append(f"        {view_name}.setOnLongClickListener(v -> {method_name}(v));")
                            else:
                                lines.append(f"        {view_name}.setOnLongClickListener(v -> {method_name}(({param_type}) v));")
                        else:
                            lines.append(f"        {view_name}.setOnLongClickListener(v -> {method_name}());")
                    else:
                        # 如果View没有在@BindView中声明，直接在构造器中获取并设置监听器
                        # 将R2.id转换为R.id
                        if resource_id.startswith('R2.id.'):
                            resource_id = resource_id.replace('R2.id.', 'R.id.')
                        if has_view_param:
                            if param_type == 'View':
                                lines.append(f"        itemView.findViewById({resource_id}).setOnLongClickListener(v -> {method_name}(v));")
                            else:
                                lines.append(f"        itemView.findViewById({resource_id}).setOnLongClickListener(v -> {method_name}(({param_type}) v));")
                        else:
                            lines.append(f"        itemView.findViewById({resource_id}).setOnLongClickListener(v -> {method_name}());")
                lines.append("")
        
        return '\n'.join(lines)
    
    def _inject_for_holder_class(self, code: str, parsed_data: Dict[str, Any]) -> str:
        """为Holder类注入初始化代码"""
        # 首先移除ButterKnife注解
        code = self._remove_butterknife_annotations(code, parsed_data)
        
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
    
    def _remove_butterknife_annotations(self, code: str, parsed_data: Dict[str, Any]) -> str:
        """移除ButterKnife注解"""
        import re
        
        # 移除@BindView注解
        bind_views = parsed_data.get('bind_views', [])
        for bind_view in bind_views:
            original_line = bind_view.get('original_line', '')
            if original_line in code:
                code = code.replace(original_line, '')
        
        # 移除@OnClick注解
        on_clicks = parsed_data.get('on_clicks', [])
        for on_click in on_clicks:
            original_line = on_click.get('original_line', '')
            if original_line in code:
                code = code.replace(original_line, '')
        
        # 移除@OnLongClick注解
        on_long_clicks = parsed_data.get('on_long_clicks', [])
        for on_long_click in on_long_clicks:
            original_line = on_long_click.get('original_line', '')
            # 使用正则表达式匹配，忽略缩进，并删除整行包括换行符
            pattern = re.escape(original_line.strip())
            code = re.sub(r'^\s*' + pattern + r'\s*\n?', '', code, flags=re.MULTILINE)
        
        return code
    
    def _has_setcontentview(self, code: str) -> bool:
        """检查是否有setContentView调用（本地或父类中）"""
        # 检查本地是否有setContentView
        if re.search(r'setContentView\s*\(', code):
            return True
        
        # 检查父类是否有setContentView（通过检查是否有getLayoutId方法）
        if re.search(r'public\s+int\s+getLayoutId\s*\(\s*\)', code):
            return True
        
        # 检查是否是常见的基类（这些基类通常有setContentView）
        common_activity_classes = [
            'BaseActivity', 'AppCompatActivity', 'Activity', 'FragmentActivity',
            'BaseFragment', 'Fragment', 'DialogFragment'
        ]
        
        # 查找类定义
        class_match = re.search(r'public\s+class\s+\w+\s+extends\s+(\w+)', code)
        if class_match:
            parent_class = class_match.group(1)
            if parent_class in common_activity_classes:
                return True
        
        return False
    
    def _inject_for_general_activity(self, code: str, parsed_data: Dict[str, Any]) -> str:
        """为普通Activity进行通用迁移处理"""
        # 移除ButterKnife注解
        code = self._remove_butterknife_annotations(code, parsed_data)
        
        # 生成initViews和initListener方法
        init_views_code = self._generate_init_views_for_general_activity(parsed_data)
        init_listener_code = self._generate_init_listener_for_general_activity(parsed_data)
        
        # 检查是否已经有initViews和initListener方法
        has_existing_initviews = self._has_method(code, 'initViews')
        has_existing_initlistener = self._has_method(code, 'initListener')
        
        # 原则1: View初始化必须在initViews方法中
        if init_views_code:
            if has_existing_initviews:
                print("DEBUG: initViews方法已存在，更新其内容")
                code = self._update_method(code, 'initViews', init_views_code)
            else:
                print("DEBUG: 创建新的initViews方法")
                code = self._create_method(code, 'initViews', init_views_code, 'protected')
        
        # 原则2: 监听器设置必须在initListener方法中
        if init_listener_code:
            if has_existing_initlistener:
                print("DEBUG: initListener方法已存在，更新其内容")
                code = self._update_method(code, 'initListener', init_listener_code)
            else:
                print("DEBUG: 创建新的initListener方法")
                code = self._create_method(code, 'initListener', init_listener_code, 'public')
        
        # 原则3: 如果有setContentView，initViews和initListener的调用需要在setContentView下面
        # 原则4: 确保不会在onCreate中直接注入View初始化和监听器代码
        if init_views_code or init_listener_code:
            print("DEBUG: 在onCreate中注入initViews和initListener方法调用")
            code = self._inject_method_calls_in_oncreate(code)
        
        # 清理onCreate方法中可能存在的重复findViewById代码和监听器设置
        code = self._clean_duplicate_findview_in_oncreate(code, parsed_data)
        
        return code
    
    def _clean_duplicate_findview_in_oncreate(self, code: str, parsed_data: Dict[str, Any]) -> str:
        """清理onCreate方法中重复的findViewById代码和OnClickListener设置"""
        print("DEBUG: 开始清理onCreate方法中重复的UI初始化代码")
        
        # 查找onCreate方法
        onCreate_pattern = r'protected\s+void\s+onCreate\s*\([^)]*\)\s*\{'
        match = re.search(onCreate_pattern, code)
        
        if not match:
            print("DEBUG: 没有找到onCreate方法")
            return code
        
        # 查找onCreate方法的结束位置
        start_pos = match.end()
        brace_count = 1
        end_pos = start_pos
        
        for i in range(start_pos, len(code)):
            if code[i] == '{':
                brace_count += 1
            elif code[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i
                    break
        
        # 获取onCreate方法的内容
        onCreate_content = code[start_pos:end_pos]
        lines = onCreate_content.split('\n')
        
        # 收集需要清理的行
        lines_to_remove = []
        
        # 定义需要清理的UI变量名
        ui_variables = [
            'listview', 'tvAll', 'tvAlltvAllDeivces', 'finddevice', 
            'tbCancel', 'tvAgent', 'tbFind', 'view_tvAgent', 'view_tvapw', 
            'view_tvRefresh', 'view_tbFind', 'view_tbCancel'
        ]
        
        # 检查onCreate方法中的每一行
        i = 0
        while i < len(lines):
            line = lines[i]
            line_stripped = line.strip()
            
            # 检查是否是重复的findViewById调用（最宽松的匹配）
            if 'findViewById(' in line and '=' in line:
                # 提取变量名（忽略缩进）
                var_name = line.strip().split('=')[0].strip()
                # 检查是否是UI变量
                if var_name in ui_variables:
                    lines_to_remove.append(i)
                    print(f"DEBUG: 标记删除重复的findViewById行: {line_stripped}")
            
            # 检查是否是重复的findViewById调用（精确匹配）
            elif 'findViewById(' in line_stripped and '=' in line_stripped:
                # 提取变量名
                if '=' in line_stripped:
                    var_name = line_stripped.split('=')[0].strip()
                    # 检查是否是UI变量
                    if var_name in ui_variables:
                        lines_to_remove.append(i)
                        print(f"DEBUG: 标记删除重复的findViewById行: {line_stripped}")
            
            # 检查是否是重复的findViewById调用（处理各种缩进格式）
            elif 'findViewById(' in line and '=' in line:
                # 提取变量名（忽略缩进）
                var_name = line.strip().split('=')[0].strip()
                # 检查是否是UI变量
                if var_name in ui_variables:
                    lines_to_remove.append(i)
                    print(f"DEBUG: 标记删除重复的findViewById行: {line_stripped}")
            
            # 检查是否是重复的OnClickListener设置
            elif 'setOnClickListener(' in line_stripped:
                # 检查是否是UI变量的监听器设置
                for var_name in ui_variables:
                    if f"{var_name}.setOnClickListener" in line_stripped:
                        # 找到这个OnClickListener块的结束位置
                        j = i
                        brace_count = 0
                        in_onclick = False
                        while j < len(lines):
                            current_line = lines[j]
                            if '{' in current_line:
                                brace_count += current_line.count('{')
                                in_onclick = True
                            if '}' in current_line:
                                brace_count -= current_line.count('}')
                                if brace_count == 0 and in_onclick:
                                    # 删除整个OnClickListener块
                                    for k in range(i, j + 1):
                                        if k not in lines_to_remove:
                                            lines_to_remove.append(k)
                                            print(f"DEBUG: 标记删除OnClickListener行: {lines[k].strip()}")
                                    i = j  # 跳过已处理的块
                                    break
                            j += 1
                        break
                # 检查是否是其他监听器设置（不限于UI变量）
                if not any(f"{var_name}.setOnClickListener" in line_stripped for var_name in ui_variables):
                    # 找到这个OnClickListener块的结束位置
                    j = i
                    brace_count = 0
                    in_onclick = False
                    while j < len(lines):
                        current_line = lines[j]
                        if '{' in current_line:
                            brace_count += current_line.count('{')
                            in_onclick = True
                        if '}' in current_line:
                            brace_count -= current_line.count('}')
                            if brace_count == 0 and in_onclick:
                                # 删除整个OnClickListener块
                                for k in range(i, j + 1):
                                    if k not in lines_to_remove:
                                        lines_to_remove.append(k)
                                        print(f"DEBUG: 标记删除OnClickListener行: {lines[k].strip()}")
                                i = j  # 跳过已处理的块
                                break
                        j += 1
            
            # 检查是否是多余的});行（但要小心不要删除OnClickListener的闭括号）
            elif line_stripped == '});' or line_stripped == '}':
                # 检查前面是否有被删除的代码
                if i > 0 and any(k in lines_to_remove for k in range(max(0, i-5), i)):
                    # 检查是否是OnClickListener的闭括号
                    is_onclick_brace = False
                    for j in range(max(0, i-10), i):
                        if j < len(lines) and 'setOnClickListener' in lines[j]:
                            is_onclick_brace = True
                            break
                    
                    if not is_onclick_brace:
                        lines_to_remove.append(i)
                        print(f"DEBUG: 标记删除多余的结束括号: {line_stripped}")
                    else:
                        print(f"DEBUG: 保留OnClickListener的闭括号: {line_stripped}")
            
            i += 1
        
        # 删除标记的行（从后往前删除，避免索引变化）
        for i in reversed(sorted(lines_to_remove)):
            if i < len(lines):
                del lines[i]
        
        if lines_to_remove:
            print(f"DEBUG: 删除了 {len(lines_to_remove)} 行重复的UI初始化代码")
            # 重新构建onCreate方法
            new_oncreate_content = '\n'.join(lines)
            return code[:start_pos] + new_oncreate_content + code[end_pos:]
        else:
            print("DEBUG: 没有找到需要清理的重复UI初始化代码")
            return code
    
    def _generate_init_views_for_general_activity(self, parsed_data: Dict[str, Any]) -> str:
        """为普通Activity生成initViews方法内容"""
        lines = []
        bind_views = parsed_data.get('bind_views', [])
        
        if bind_views:
            lines.append("        // 初始化View绑定 - 替换@BindView注解")
            for bind_view in bind_views:
                field_name = bind_view['name']
                resource_id = bind_view['id']
                # 将R2.id转换为R.id
                if resource_id.startswith('R2.id.'):
                    resource_id = resource_id.replace('R2.id.', 'R.id.')
                lines.append(f"        {field_name} = findViewById({resource_id});")
        
        return '\n'.join(lines)
    
    def _generate_init_listener_for_general_activity(self, parsed_data: Dict[str, Any]) -> str:
        """为普通Activity生成initListener方法内容"""
        lines = []
        on_clicks = parsed_data.get('on_clicks', [])
        on_long_clicks = parsed_data.get('on_long_clicks', [])
        
        if on_clicks:
            lines.append("        // 初始化点击事件 - 替换@OnClick注解")
            for on_click in on_clicks:
                resource_ids = on_click['ids']
                method_name = on_click['method']
                has_view_param = on_click.get('has_view_param', False)
                
                for resource_id in resource_ids:
                    # 将R2.id转换为R.id
                    if resource_id.startswith('R2.id.'):
                        resource_id = resource_id.replace('R2.id.', 'R.id.')
                    if has_view_param:
                        lines.append(f"        findViewById({resource_id}).setOnClickListener(v -> {method_name}(v));")
                    else:
                        lines.append(f"        findViewById({resource_id}).setOnClickListener(v -> {method_name}());")
        
        if on_long_clicks:
            lines.append("        // 初始化长按事件 - 替换@OnLongClick注解")
            for on_long_click in on_long_clicks:
                resource_ids = on_long_click['ids']
                method_name = on_long_click['method']
                has_view_param = on_long_click.get('has_view_param', False)
                
                for resource_id in resource_ids:
                    # 将R2.id转换为R.id
                    if resource_id.startswith('R2.id.'):
                        resource_id = resource_id.replace('R2.id.', 'R.id.')
                    if has_view_param:
                        lines.append(f"        findViewById({resource_id}).setOnLongClickListener(v -> {method_name}(v));")
                    else:
                        lines.append(f"        findViewById({resource_id}).setOnLongClickListener(v -> {method_name}());")
        
        return '\n'.join(lines)
    
    def _has_method(self, code: str, method_name: str) -> bool:
        """检查方法是否存在"""
        pattern = rf'(public|protected|private)\s+.*\s+{re.escape(method_name)}\s*\('
        return bool(re.search(pattern, code))
    
    def _update_method(self, code: str, method_name: str, new_content: str) -> str:
        """更新现有方法的内容 - 在现有代码末尾追加"""
        lines = code.split('\n')
        method_start = -1
        method_end = -1
        brace_count = 0
        in_method = False
        
        for i, line in enumerate(lines):
            # 查找方法开始
            if re.search(rf'(public|protected|private)\s+.*\s+{re.escape(method_name)}\s*\(', line):
                method_start = i
                in_method = True
                # 开始计算大括号
                for char in line:
                    if char == '{':
                        brace_count += 1
                continue
            
            if in_method:
                # 计算大括号
                for char in line:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            method_end = i
                            break
                
                if method_end != -1:
                    break
        
        if method_start != -1 and method_end != -1:
            # 对于initListener方法，完全替换内容以避免重复代码
            if method_name == 'initListener':
                print(f"DEBUG: 完全替换{method_name}方法内容")
                new_content_lines = new_content.split('\n')
                new_lines = lines[:method_start+1] + new_content_lines + lines[method_end:]
                return '\n'.join(new_lines)
            
            # 对于其他方法，在方法结束前（最后一个}之前）追加新内容
            # 检查是否已经有ButterKnife迁移的注释，避免重复添加
            existing_content = '\n'.join(lines[method_start + 1:method_end])
            if "// 初始化View绑定 - 替换@BindView注解" in existing_content or "// 初始化点击事件 - 替换@OnClick注解" in existing_content:
                print(f"DEBUG: {method_name}方法中已存在ButterKnife迁移代码，跳过追加")
                return code
            
            # 检查是否已经有相同的findViewById代码，避免重复添加
            if method_name == 'initViews':
                # 检查是否已经有相同的findViewById调用
                new_lines_list = new_content.split('\n')
                for new_line in new_lines_list:
                    if 'findViewById(' in new_line and new_line.strip() in existing_content:
                        print(f"DEBUG: {method_name}方法中已存在相同的findViewById调用，跳过重复添加")
                        return code
            
            # 在方法结束前追加新内容，保持原有代码
            new_lines = lines[:method_end] + [new_content] + lines[method_end:]
            return '\n'.join(new_lines)
        
        return code
    
    def _create_method(self, code: str, method_name: str, content: str, visibility: str) -> str:
        """创建新方法"""
        # 查找类的结束位置
        class_end = self._find_class_end(code)
        print(f"DEBUG: 查找类结束位置: {class_end}")
        if class_end == -1:
            print("DEBUG: 未找到类结束位置，尝试使用备用方法")
            # 备用方法：查找最后一个独立的}
            last_brace = code.rfind('}')
            if last_brace != -1:
                class_end = last_brace + 1
                print(f"DEBUG: 使用备用方法找到类结束位置: {class_end}")
            else:
                print("DEBUG: 无法找到类结束位置，无法创建方法")
                return code
        
        # 生成方法
        method = f"\n    {visibility} void {method_name}() {{\n{content}\n    }}"
        print(f"DEBUG: 创建方法: {method}")
        
        # 在类结束前插入方法（在最后一个}之前）
        # 使用字符位置而不是行号，更精确
        before_end = code[:class_end-1]  # 在最后一个}之前
        after_end = code[class_end-1:]   # 从最后一个}开始
        
        return before_end + method + "\n" + after_end
    
    def _find_class_end(self, code: str) -> int:
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
    
    def _inject_method_calls_in_oncreate(self, code: str) -> str:
        """在onCreate方法中注入initViews和initListener调用"""
        print("DEBUG: 开始注入initViews和initListener调用")
        # 查找onCreate方法
        onCreate_pattern = r'protected\s+void\s+onCreate\s*\([^)]*\)\s*\{'
        match = re.search(onCreate_pattern, code)
        
        if not match:
            print("DEBUG: 没有找到onCreate方法")
            return code
        
        print(f"DEBUG: 找到onCreate方法，位置: {match.start()}-{match.end()}")
        
        # 查找onCreate方法的结束位置
        start_pos = match.end()
        brace_count = 1
        end_pos = start_pos
        
        for i in range(start_pos, len(code)):
            if code[i] == '{':
                brace_count += 1
            elif code[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i
                    break
        
        # 检查onCreate方法中是否已经存在调用
        onCreate_content = code[start_pos:end_pos]
        # 更精确的检查：确保initViews()和initListener()都在onCreate方法中
        has_initviews = 'initViews();' in onCreate_content
        has_initlistener = 'initListener();' in onCreate_content
        if has_initviews and has_initlistener:
            print("DEBUG: onCreate方法中initViews和initListener调用已存在，跳过注入")
            return code
        
        # 查找setContentView调用，确保initViews和initListener调用在setContentView下面
        setcontentview_pattern = re.compile(r'setContentView\s*\([^)]*\)\s*;', re.MULTILINE)
        setcontentview_match = setcontentview_pattern.search(code, start_pos, end_pos)
        
        if setcontentview_match:
            # 在setContentView之后注入方法调用
            injection_position = setcontentview_match.end()
            print(f"DEBUG: 在setContentView之后注入方法调用，位置: {injection_position}")
        else:
            # 如果没有找到setContentView，在onCreate方法末尾注入
            injection_position = end_pos
            print("DEBUG: 没有找到setContentView，在onCreate方法末尾注入")
        
        # 在onCreate方法中添加调用
        if has_initviews and not has_initlistener:
            # 只有initViews()，添加initListener()
            method_calls = "\n        initListener();"
        elif not has_initviews and has_initlistener:
            # 只有initListener()，添加initViews()
            method_calls = "\n        initViews();"
        elif not has_initviews and not has_initlistener:
            # 都没有，添加两个
            method_calls = "\n        initViews();\n        initListener();"
        else:
            # 都有，不需要添加
            method_calls = ""
        
        if method_calls:
            return code[:injection_position] + method_calls + code[injection_position:]
        else:
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
            if 'Holder' in class_name and ('BaseHolder' in extends or 'RecyclerView' in extends):
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
        class_pattern = re.compile(r'class\s+(\w+)(?:\s+extends\s+([\w.]+))?', re.MULTILINE)
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
        """找到主类的真正结束位置（排除内部类）"""
        # 直接使用_find_class_end方法
        return self._find_class_end(code)
    
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
            stripped_line = line.strip()
            if stripped_line.startswith('import'):
                # 精确匹配以import butterknife开头的语句
                if stripped_line.startswith('import butterknife'):
                    print(f"DEBUG: 移除ButterKnife import语句: {stripped_line}")
                    continue
                # 也检查其他ButterKnife相关的import（以防有变体）
                elif ('butterknife' in stripped_line.lower() or 
                      any(annotation in stripped_line for annotation in [
                          'BindView', 'OnClick', 'BindString', 'BindColor', 
                          'BindDimen', 'BindDrawable', 'BindBitmap', 'BindInt', 
                          'BindFloat', 'BindBoolean', 'BindArray', 'BindFont', 
                          'BindAnim', 'BindAnimator', 'BindBool'
                      ])):
                    print(f"DEBUG: 移除ButterKnife相关import语句: {stripped_line}")
                    continue
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
