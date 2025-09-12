#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from butterknife_parser_module.butterknife_parser import ButterKnifeParser

def test_parser_debug():
    """测试解析器调试"""
    
    # 读取实际文件
    file_path = "tests/Agent_DeviceListActivity.java"
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    print("=== 测试解析器 ===")
    
    # 创建解析器
    parser = ButterKnifeParser()
    
    # 解析代码
    parsed_data = parser.parse(code)
    
    print(f"解析结果:")
    print(f"  - @BindView注解数量: {len(parsed_data.get('bind_views', []))}")
    print(f"  - @OnClick注解数量: {len(parsed_data.get('on_clicks', []))}")
    print(f"  - ButterKnife.bind调用: {parsed_data.get('bind_call', False)}")
    
    if parsed_data.get('on_clicks'):
        print(f"  - @OnClick详情:")
        for i, on_click in enumerate(parsed_data['on_clicks']):
            print(f"    {i+1}. 方法: {on_click['method']}")
            print(f"       资源ID: {on_click['ids']}")
            print(f"       有View参数: {on_click.get('has_view_param', False)}")

if __name__ == "__main__":
    test_parser_debug()
