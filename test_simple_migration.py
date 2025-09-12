#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import migrate_file

def test_simple_migration():
    """测试简单迁移"""
    
    file_path = "tests/Agent_DeviceListActivity.java"
    print(f"开始迁移文件: {file_path}")
    
    try:
        result = migrate_file(file_path)
        print(f"迁移结果: {result}")
        
        # 检查迁移后的文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否还有ButterKnife注解
        if '@BindView' in content or '@OnClick' in content:
            print("❌ 迁移失败：仍然存在ButterKnife注解")
        else:
            print("✅ ButterKnife注解已移除")
        
        # 检查是否有findViewById调用
        if 'findViewById' in content:
            print("✅ 已生成findViewById调用")
        else:
            print("❌ 未生成findViewById调用")
        
        # 检查是否有setOnClickListener调用
        if 'setOnClickListener' in content:
            print("✅ 已生成setOnClickListener调用")
        else:
            print("❌ 未生成setOnClickListener调用")
        
        # 检查是否有initViews和initListener方法
        if 'initViews()' in content:
            print("✅ 已生成initViews方法调用")
        else:
            print("❌ 未生成initViews方法调用")
            
        if 'initListener()' in content:
            print("✅ 已生成initListener方法调用")
        else:
            print("❌ 未生成initListener方法调用")
            
    except Exception as e:
        print(f"❌ 迁移过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_migration()
