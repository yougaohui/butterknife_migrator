#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ButterKnife注解解析器
使用正则表达式提取ButterKnife注解信息
输出结构化数据
"""

import re
from typing import Dict, List, Optional, Tuple


class ButterKnifeParser:
    """ButterKnife注解解析器类"""
    
    def __init__(self):
        # 编译正则表达式以提高性能
        # 支持同一行和多行格式的@BindView注解
        self.bind_view_pattern = re.compile(
            r'@BindView\s*\(\s*(R2?\.id\.\w+)\s*\)\s+(?:public\s+|private\s+|protected\s+)?(\w+)\s+(\w+)\s*;',
            re.MULTILINE
        )
        
        self.on_click_pattern = re.compile(
            r'@OnClick\s*\(\s*(?:\{\s*)?((?:R2?\.id\.\w+(?:\s*,\s*R2?\.id\.\w+)*)?)(?:\s*\})?\s*\)\s*(?:public\s+)?(?:void\s+)?(\w+)\s*\([^)]*\)',
            re.MULTILINE
        )
        
        self.on_long_click_pattern = re.compile(
            r'@OnLongClick\s*\(\s*([^)]+)\s*\)\s*(?:public\s+)?(?:boolean\s+)?(\w+)\s*\([^)]*\)',
            re.MULTILINE
        )
        
        self.bind_call_pattern = re.compile(
            r'ButterKnife\.bind\s*\(\s*this\s*\)\s*;',
            re.MULTILINE
        )
        
        self.import_pattern = re.compile(
            r'import\s+butterknife\.BindView\s*;',
            re.MULTILINE
        )
        
        self.onclick_import_pattern = re.compile(
            r'import\s+butterknife\.OnClick\s*;',
            re.MULTILINE
        )
        
        self.onlongclick_import_pattern = re.compile(
            r'import\s+butterknife\.OnLongClick\s*;',
            re.MULTILINE
        )
        
        self.butterknife_import_pattern = re.compile(
            r'import\s+butterknife\.ButterKnife\s*;',
            re.MULTILINE
        )
        
        self.class_pattern = re.compile(
            r'class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?',
            re.MULTILINE
        )
        
        self.method_pattern = re.compile(
            r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?\w+\s+(\w+)\s*\([^)]*\)\s*\{',
            re.MULTILINE
        )
    
    def parse(self, content: str) -> Dict:
        """解析Java文件内容，提取ButterKnife注解信息"""
        result = {
            'has_butterknife': False,
            'bind_views': [],
            'on_clicks': [],
            'on_long_clicks': [],
            'bind_call': False,
            'imports': {
                'bindview': False,
                'onclick': False,
                'onlongclick': False,
                'butterknife': False
            },
            'class_info': {},
            'methods': []
        }
        
        try:
            # 检查是否包含ButterKnife注解
            if self._has_butterknife_annotations(content):
                result['has_butterknife'] = True
                
                # 解析@BindView注解
                result['bind_views'] = self._parse_bind_views(content)
                
                # 解析@OnClick注解
                result['on_clicks'] = self._parse_on_clicks(content)
                
                # 解析@OnLongClick注解
                result['on_long_clicks'] = self._parse_on_long_clicks(content)
                
                # 检查ButterKnife.bind调用
                result['bind_call'] = self._has_bind_call(content)
                
                # 检查import语句
                result['imports'] = self._parse_imports(content)
                
                # 解析类信息
                result['class_info'] = self._parse_class_info(content)
                
                # 解析方法信息
                result['methods'] = self._parse_methods(content)
        
        except Exception as e:
            print(f"解析ButterKnife注解时出错: {e}")
        
        return result
    
    def _has_butterknife_annotations(self, content: str) -> bool:
        """检查是否包含ButterKnife注解"""
        return (
            '@BindView' in content or
            '@OnClick' in content or
            '@OnLongClick' in content or
            'ButterKnife.bind' in content
        )
    
    def _parse_bind_views(self, content: str) -> List[Dict]:
        """解析@BindView注解"""
        bind_views = []
        # 过滤掉注释掉的代码
        filtered_content = self._remove_commented_code(content)
        matches = self.bind_view_pattern.findall(filtered_content)
        
        for match in matches:
            resource_id, field_type, field_name = match
            bind_views.append({
                'id': resource_id.strip(),
                'type': field_type.strip(),
                'name': field_name.strip(),
                'original_line': self._find_original_line(content, match[0])
            })
        
        return bind_views
    
    def _parse_on_clicks(self, content: str) -> List[Dict]:
        """解析@OnClick注解"""
        on_clicks = []
        # 过滤掉注释掉的代码
        filtered_content = self._remove_commented_code(content)
        matches = self.on_click_pattern.findall(filtered_content)
        
        for match in matches:
            resource_ids_str, method_name = match
            
            # 解析资源ID列表
            if resource_ids_str.strip():
                resource_ids = [
                    rid.strip() for rid in resource_ids_str.split(',')
                ]
            else:
                resource_ids = []
            
            # 检测方法是否有View参数
            has_view_param, param_type = self._check_method_has_view_param(content, method_name.strip())
            
            on_clicks.append({
                'ids': resource_ids,
                'method': method_name.strip(),
                'has_view_param': has_view_param,
                'param_type': param_type,
                'original_line': self._find_original_line(content, match[0])
            })
        
        return on_clicks
    
    def _parse_on_long_clicks(self, content: str) -> List[Dict]:
        """解析@OnLongClick注解"""
        on_long_clicks = []
        matches = self.on_long_click_pattern.findall(content)
        
        for match in matches:
            resource_ids_str, method_name = match
            
            # 解析资源ID列表
            if resource_ids_str.strip():
                # 处理单个ID或多个ID的情况
                if ',' in resource_ids_str:
                    resource_ids = [rid.strip() for rid in resource_ids_str.split(',')]
                else:
                    resource_ids = [resource_ids_str.strip()]
            else:
                resource_ids = []
            
            # 检测方法是否有View参数
            has_view_param, param_type = self._check_method_has_view_param(content, method_name.strip())
            
            on_long_clicks.append({
                'ids': resource_ids,
                'method': method_name.strip(),
                'has_view_param': has_view_param,
                'param_type': param_type,
                'original_line': self._find_original_line(content, match[0])
            })
        
        return on_long_clicks
    
    def _check_method_has_view_param(self, content: str, method_name: str) -> Tuple[bool, str]:
        """检查方法是否有View参数，并返回参数类型"""
        # 查找主类中的方法定义，使用更严谨的方法边界检测
        method_start, method_end = self._find_method_boundaries(content, method_name)
        
        if method_start != -1 and method_end != -1:
            # 提取方法签名
            method_signature = content[method_start:method_end].split('{')[0]
            # 提取参数部分
            param_match = re.search(r'\(([^)]*)\)', method_signature)
            if param_match:
                params = param_match.group(1).strip()
                if params:
                    # 检查参数中是否包含View类型（包括所有View子类）
                    param_type = self._extract_view_param_type(params)
                    if param_type != 'View' or 'View' in params:
                        return True, param_type
                    else:
                        return False, ""
                else:
                    return False, ""
        
        return False, ""
    
    def _find_method_boundaries(self, content: str, method_name: str) -> Tuple[int, int]:
        """查找方法的开始和结束位置，使用严谨的大括号匹配算法"""
        lines = content.split('\n')
        
        # 查找方法开始位置
        method_start = -1
        for i, line in enumerate(lines):
            # 查找主类中的方法定义（不在匿名内部类中）
            if re.match(rf'^\s*(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:void\s+|boolean\s+)?{re.escape(method_name)}\s*\([^)]*\)\s*{{', line):
                method_start = sum(len(lines[j]) + 1 for j in range(i))
                break
        
        if method_start == -1:
            return -1, -1
        
        # 使用严谨的大括号匹配算法查找方法结束位置
        brace_count = 0
        in_method = False
        method_end = -1
        
        for i, char in enumerate(content[method_start:], method_start):
            if char == '{':
                brace_count += 1
                if brace_count == 1:
                    in_method = True
            elif char == '}':
                brace_count -= 1
                if in_method and brace_count == 0:
                    method_end = i + 1
                    break
        
        return method_start, method_end
    
    def _remove_commented_code(self, content: str) -> str:
        """移除注释掉的代码，使用更严谨的注释处理"""
        lines = content.split('\n')
        filtered_lines = []
        in_block_comment = False
        
        for line in lines:
            # 处理块注释
            if '/*' in line and '*/' in line:
                # 单行块注释，跳过
                continue
            elif '/*' in line:
                # 块注释开始
                in_block_comment = True
                # 保留块注释前的代码
                before_comment = line.split('/*')[0]
                if before_comment.strip():
                    filtered_lines.append(before_comment)
                continue
            elif '*/' in line:
                # 块注释结束
                in_block_comment = False
                # 保留块注释后的代码
                after_comment = line.split('*/')[1]
                if after_comment.strip():
                    filtered_lines.append(after_comment)
                continue
            elif in_block_comment:
                # 在块注释中，跳过
                continue
            
            # 处理行注释
            if '//' in line:
                # 保留注释前的代码
                before_comment = line.split('//')[0]
                if before_comment.strip():
                    filtered_lines.append(before_comment)
            else:
                # 检查是否是注释行
                stripped = line.strip()
                if stripped.startswith('//') or stripped.startswith('*'):
                    # 跳过注释行
                    continue
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _extract_view_param_type(self, params: str) -> str:
        """从参数中提取View类型"""
        # 常见的View类型
        view_types = [
            'TextView', 'Button', 'ImageView', 'EditText', 'CheckBox', 'RadioButton',
            'Switch', 'SeekBar', 'ProgressBar', 'Spinner', 'ListView', 'RecyclerView',
            'LinearLayout', 'RelativeLayout', 'FrameLayout', 'ConstraintLayout',
            'CardView', 'ScrollView', 'NestedScrollView', 'ViewPager', 'TabLayout',
            'Toolbar', 'AppBarLayout', 'CoordinatorLayout', 'DrawerLayout',
            'NavigationView', 'BottomNavigationView', 'FloatingActionButton'
        ]
        
        # 查找参数中的View类型
        for view_type in view_types:
            if view_type in params:
                return view_type
        
        # 如果没有找到具体的View类型，返回通用的View
        return 'View'
    
    def _has_bind_call(self, content: str) -> bool:
        """检查是否包含ButterKnife.bind调用"""
        return bool(self.bind_call_pattern.search(content))
    
    def _parse_imports(self, content: str) -> Dict[str, bool]:
        """解析import语句"""
        return {
            'bindview': bool(self.import_pattern.search(content)),
            'onclick': bool(self.onclick_import_pattern.search(content)),
            'onlongclick': bool(self.onlongclick_import_pattern.search(content)),
            'butterknife': bool(self.butterknife_import_pattern.search(content))
        }
    
    def _parse_class_info(self, content: str) -> Dict:
        """解析类信息"""
        class_info = {}
        match = self.class_pattern.search(content)
        
        if match:
            class_info = {
                'name': match.group(1),
                'extends': match.group(2) if match.group(2) else None,
                'implements': match.group(3).strip() if match.group(3) else None
            }
        
        return class_info
    
    def _parse_methods(self, content: str) -> List[str]:
        """解析方法信息"""
        methods = []
        matches = self.method_pattern.findall(content)
        
        for match in matches:
            method_name = match.strip()
            if method_name and method_name not in methods:
                methods.append(method_name)
        
        return methods
    
    def _find_original_line(self, content: str, pattern: str) -> Optional[str]:
        """查找原始行内容"""
        lines = content.split('\n')
        
        for line in lines:
            if pattern in line:
                return line.strip()
        
        return None
    
    def get_parsing_statistics(self, parsed_data: Dict) -> Dict:
        """获取解析统计信息"""
        stats = {
            'total_bind_views': len(parsed_data.get('bind_views', [])),
            'total_on_clicks': len(parsed_data.get('on_clicks', [])),
            'has_bind_call': parsed_data.get('bind_call', False),
            'imports_count': sum(parsed_data.get('imports', {}).values()),
            'class_type': self._determine_class_type(parsed_data.get('class_info', {}))
        }
        
        return stats
    
    def _determine_class_type(self, class_info: Dict) -> str:
        """确定类类型"""
        if not class_info:
            return 'unknown'
        
        extends = class_info.get('extends', '')
        implements = class_info.get('implements', '')
        
        if 'Activity' in extends:
            return 'Activity'
        elif 'Fragment' in extends:
            return 'Fragment'
        elif 'Adapter' in extends or 'Adapter' in implements:
            return 'Adapter'
        elif 'View' in extends:
            return 'View'
        else:
            return 'Other'
    
    def validate_parsed_data(self, parsed_data: Dict) -> Tuple[bool, List[str]]:
        """验证解析的数据"""
        errors = []
        
        # 检查必需字段
        if not parsed_data.get('has_butterknife'):
            errors.append("未检测到ButterKnife注解")
        
        # 检查@BindView注解的完整性
        for bind_view in parsed_data.get('bind_views', []):
            if not all(key in bind_view for key in ['id', 'type', 'name']):
                errors.append(f"@BindView注解信息不完整: {bind_view}")
        
        # 检查@OnClick注解的完整性
        for on_click in parsed_data.get('on_clicks', []):
            if not all(key in on_click for key in ['ids', 'method']):
                errors.append(f"@OnClick注解信息不完整: {on_click}")
        
        return len(errors) == 0, errors


class ParsingResult:
    """解析结果类"""
    
    def __init__(self, parsed_data: Dict):
        self.data = parsed_data
        self.parser = ButterKnifeParser()
    
    def is_valid(self) -> bool:
        """检查解析结果是否有效"""
        is_valid, _ = self.parser.validate_parsed_data(self.data)
        return is_valid
    
    def get_bind_views_count(self) -> int:
        """获取@BindView注解数量"""
        return len(self.data.get('bind_views', []))
    
    def get_on_clicks_count(self) -> int:
        """获取@OnClick注解数量"""
        return len(self.data.get('on_clicks', []))
    
    def has_bind_call(self) -> bool:
        """是否有ButterKnife.bind调用"""
        return self.data.get('bind_call', False)
    
    def get_class_type(self) -> str:
        """获取类类型"""
        return self.parser._determine_class_type(self.data.get('class_info', {}))
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return self.parser.get_parsing_statistics(self.data)
    
    def __str__(self) -> str:
        """字符串表示"""
        stats = self.get_statistics()
        return f"""解析结果:
类类型: {stats['class_type']}
@BindView注解: {stats['total_bind_views']} 个
@OnClick注解: {stats['total_on_clicks']} 个
ButterKnife.bind调用: {'是' if stats['has_bind_call'] else '否'}
"""
