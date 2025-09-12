#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from transformer.findview_transformer import FindViewTransformer

def test_bindview_removal():
    """测试@BindView注解移除功能"""
    
    # 测试代码
    test_code = """public class TestActivity extends Activity {
    @BindView(R.id.listview) ListView listview;
    @BindView(R.id.tvAll) TextView tvAll;
    @BindView(R.id.tvAgent) TextView tvAgent;
    private String test;
}"""
    
    print("原始代码:")
    print(test_code)
    print("\n" + "="*50 + "\n")
    
    # 创建转换器
    transformer = FindViewTransformer()
    
    # 模拟解析数据
    parsed_data = {
        'bind_views': [
            {'type': 'ListView', 'name': 'listview', 'id': 'R.id.listview'},
            {'type': 'TextView', 'name': 'tvAll', 'id': 'R.id.tvAll'},
            {'type': 'TextView', 'name': 'tvAgent', 'id': 'R.id.tvAgent'}
        ]
    }
    
    # 执行转换
    result = transformer.transform(parsed_data, test_code)
    
    print("转换后代码:")
    print(result)
    print("\n" + "="*50 + "\n")
    
    # 检查结果
    if "@BindView" in result:
        print("❌ @BindView注解没有被移除!")
        return False
    else:
        print("✅ @BindView注解被成功移除!")
        return True

if __name__ == "__main__":
    test_bindview_removal()
