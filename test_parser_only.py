#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from butterknife_parser_module.butterknife_parser import ButterKnifeParser

def test_parser_only():
    """只测试解析器"""
    
    file_path = "tests/Agent_DeviceListActivity.java"
    print(f"测试解析器: {file_path}")
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 创建解析器
    parser = ButterKnifeParser()
    
    # 解析
    parsed_data = parser.parse(content)
    
    print(f"解析结果:")
    print(f"  - has_butterknife: {parsed_data.get('has_butterknife', False)}")
    print(f"  - bind_views: {len(parsed_data.get('bind_views', []))}")
    print(f"  - on_clicks: {len(parsed_data.get('on_clicks', []))}")
    print(f"  - bind_call: {parsed_data.get('bind_call', False)}")
    
    if parsed_data.get('bind_views'):
        print(f"  - @BindView详情:")
        for i, bind_view in enumerate(parsed_data['bind_views']):
            print(f"    {i+1}. {bind_view['name']} = {bind_view['id']} ({bind_view['type']})")
    
    if parsed_data.get('on_clicks'):
        print(f"  - @OnClick详情:")
        for i, on_click in enumerate(parsed_data['on_clicks']):
            print(f"    {i+1}. 方法: {on_click['method']}")
            print(f"       资源ID: {on_click['ids']}")
            print(f"       有View参数: {on_click.get('has_view_param', False)}")

if __name__ == "__main__":
    test_parser_only()
