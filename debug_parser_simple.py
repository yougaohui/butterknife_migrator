#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_regex_patterns():
    """测试正则表达式模式"""
    
    # 测试内容
    test_content = """
    @BindView(R.id.listview) ListView listview;
    @BindView(R.id.tvAll) TextView tvAll;
    @OnClick({R.id.tvAgent, R.id.tvapw, R.id.tvRefresh})
    public void onClick(View view) {
        // 方法内容
    }
    """
    
    print("测试内容:")
    print(test_content)
    print("=" * 50)
    
    # 测试@BindView模式
    bind_view_pattern = re.compile(
        r'@BindView\s*\(\s*(R2?\.id\.\w+)\s*\)\s+(?:public\s+|private\s+|protected\s+)?(\w+)\s+(\w+)\s*;',
        re.MULTILINE
    )
    
    print("测试@BindView模式:")
    matches = bind_view_pattern.findall(test_content)
    print(f"匹配结果: {matches}")
    
    # 测试@OnClick模式
    on_click_pattern = re.compile(
        r'@OnClick\s*\(\s*(?:\{\s*)?((?:R2?\.id\.\w+(?:\s*,\s*R2?\.id\.\w+)*)?)(?:\s*\})?\s*\)\s*(?:public\s+)?(?:void\s+)?(\w+)\s*\([^)]*\)',
        re.MULTILINE
    )
    
    print("测试@OnClick模式:")
    matches = on_click_pattern.findall(test_content)
    print(f"匹配结果: {matches}")

if __name__ == "__main__":
    test_regex_patterns()
