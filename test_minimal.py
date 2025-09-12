#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 直接导入和测试
try:
    from butterknife_parser_module.butterknife_parser import ButterKnifeParser
    print("✅ 解析器导入成功")
    
    # 读取文件
    with open("tests/Agent_DeviceListActivity.java", 'r', encoding='utf-8') as f:
        content = f.read()
    print("✅ 文件读取成功")
    
    # 创建解析器
    parser = ButterKnifeParser()
    print("✅ 解析器创建成功")
    
    # 解析
    parsed_data = parser.parse(content)
    print("✅ 解析完成")
    
    print(f"解析结果: {parsed_data}")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
