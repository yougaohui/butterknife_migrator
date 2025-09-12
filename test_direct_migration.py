#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_direct_migration():
    """直接测试迁移"""
    
    # 读取文件
    file_path = "tests/Agent_DeviceListActivity.java"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"文件长度: {len(content)}")
    print(f"包含@BindView: {'@BindView' in content}")
    print(f"包含@OnClick: {'@OnClick' in content}")
    
    # 导入迁移工具
    try:
        from auto_migrate import AutoButterKnifeMigrator
        print("✅ 迁移工具导入成功")
        
        # 创建迁移器
        migrator = AutoButterKnifeMigrator()
        print("✅ 迁移器创建成功")
        
        # 直接调用迁移方法
        result = migrator.migrate()
        print(f"迁移结果: {result}")
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_migration()
