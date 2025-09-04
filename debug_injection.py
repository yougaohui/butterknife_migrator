#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试代码注入逻辑
"""

import re

# 全局测试代码
TEST_CODE = '''    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        // 绑定ButterKnife
        // 其他初始化代码
        titleText.setText("Hello World");
    }'''

def test_oncreate_pattern():
    """测试onCreate正则表达式"""
    pattern = re.compile(
        r'(\s*@Override\s*\n?\s*protected\s+void\s+onCreate\s*\([^)]*\)\s*\{)',
        re.MULTILINE
    )
    
    match = pattern.search(TEST_CODE)
    print("onCreate pattern test:")
    print(f"Match found: {match is not None}")
    if match:
        print(f"Match: {repr(match.group(0))}")
        print(f"Start: {match.start()}, End: {match.end()}")
    
    return match

def test_method_end_finding():
    """测试方法结束位置查找"""
    # 模拟_find_method_end逻辑
    start_pos = TEST_CODE.find('{') + 1
    brace_count = 0
    
    for i, char in enumerate(TEST_CODE[start_pos:], start_pos):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                print(f"Method end found at position: {i + 1}")
                print(f"Code before end: {repr(TEST_CODE[:i+1])}")
                print(f"Code after end: {repr(TEST_CODE[i+1:])}")
                return i + 1
    
    return start_pos

if __name__ == "__main__":
    print("=== 调试代码注入逻辑 ===")
    
    # 测试onCreate正则表达式
    match = test_oncreate_pattern()
    
    if match:
        print("\n=== 测试方法结束位置查找 ===")
        method_end = test_method_end_finding()
        
        # 测试注入逻辑
        injection_code = '''        // 初始化View绑定
        titleText = (TextView) findViewById(R.id.title_text);
        submitButton = (Button) findViewById(R.id.submit_button);
        cancelButton = (Button) findViewById(R.id.cancel_button);

        // 初始化点击事件
        submitButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                onButtonClick(v);
            }
        });'''
        
        print(f"\n=== 测试代码注入 ===")
        print(f"原始代码长度: {len(TEST_CODE)}")
        print(f"onCreate开始: {match.end()}")
        print(f"onCreate结束: {method_end}")
        
        if method_end > match.end():
            before_end = TEST_CODE[:method_end]
            after_end = TEST_CODE[method_end:]
            
            new_code = before_end + '\n' + injection_code + '\n    ' + after_end
            print(f"\n=== 注入后的代码 ===")
            print(new_code)
