#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from butterknife_parser_module.butterknife_parser import ButterKnifeParser
from transformer.findview_transformer import FindViewTransformer
from transformer.onclick_transformer import OnClickTransformer
from transformer.bindcall_remover import BindCallRemover

def test_real_migration():
    """测试真实的迁移过程"""
    
    # 读取实际文件
    file_path = "tests/Agent_DeviceListActivity.java"
    with open(file_path, 'r', encoding='utf-8') as f:
        original_code = f.read()
    
    print("=== 步骤1: 解析ButterKnife注解 ===")
    parser = ButterKnifeParser()
    parsed_data = parser.parse(original_code)
    
    print(f"解析结果:")
    print(f"  - @BindView注解数量: {len(parsed_data.get('bind_views', []))}")
    print(f"  - @OnClick注解数量: {len(parsed_data.get('on_clicks', []))}")
    print(f"  - ButterKnife.bind调用: {parsed_data.get('bind_call', False)}")
    
    if parsed_data.get('bind_views'):
        print(f"  - @BindView详情:")
        for i, bind_view in enumerate(parsed_data['bind_views']):
            print(f"    {i+1}. {bind_view['type']} {bind_view['name']} = {bind_view['id']}")
    
    print("\n=== 步骤2: 应用FindViewTransformer ===")
    findview_transformer = FindViewTransformer()
    if findview_transformer.can_transform(parsed_data):
        print("✅ FindViewTransformer可以转换")
        transformed_code = findview_transformer.transform(parsed_data, original_code)
        
        # 检查@BindView是否被移除
        bindview_count = transformed_code.count('@BindView')
        print(f"转换后@BindView注解数量: {bindview_count}")
        
        if bindview_count == 0:
            print("✅ @BindView注解被成功移除!")
        else:
            print("❌ @BindView注解没有被完全移除!")
            # 显示剩余的@BindView
            lines = transformed_code.split('\n')
            for i, line in enumerate(lines):
                if '@BindView' in line:
                    print(f"  第{i+1}行: {line.strip()}")
    else:
        print("❌ FindViewTransformer无法转换")
    
    print("\n=== 步骤3: 应用OnClickTransformer ===")
    onclick_transformer = OnClickTransformer()
    if onclick_transformer.can_transform(parsed_data):
        print("✅ OnClickTransformer可以转换")
        transformed_code = onclick_transformer.transform(parsed_data, transformed_code)
        
        # 检查@OnClick是否被移除
        onclick_count = transformed_code.count('@OnClick')
        print(f"转换后@OnClick注解数量: {onclick_count}")
        
        if onclick_count == 0:
            print("✅ @OnClick注解被成功移除!")
        else:
            print("❌ @OnClick注解没有被完全移除!")
    else:
        print("❌ OnClickTransformer无法转换")
    
    print("\n=== 步骤4: 应用BindCallRemover ===")
    bindcall_remover = BindCallRemover()
    if bindcall_remover.can_transform(parsed_data):
        print("✅ BindCallRemover可以转换")
        transformed_code = bindcall_remover.transform(parsed_data, transformed_code)
        
        # 检查ButterKnife.bind是否被移除
        bindcall_count = transformed_code.count('ButterKnife.bind')
        print(f"转换后ButterKnife.bind调用数量: {bindcall_count}")
        
        if bindcall_count == 0:
            print("✅ ButterKnife.bind调用被成功移除!")
        else:
            print("❌ ButterKnife.bind调用没有被完全移除!")
    else:
        print("❌ BindCallRemover无法转换")

if __name__ == "__main__":
    test_real_migration()
