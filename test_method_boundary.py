#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from butterknife_parser_module.butterknife_parser import ButterKnifeParser

def test_method_boundary():
    """测试方法边界检测"""
    
    # 测试代码，包含onClick方法和注释掉的代码
    test_code = """
public class TestActivity {
    @OnClick({R.id.button1, R.id.button2})
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.button1:
                // 这是注释
                doSomething();
                break;
            case R.id.button2:
                /* 这是块注释
                 * 多行注释
                 */
                doSomethingElse();
                break;
            /*case R.id.button3:
                // 注释掉的代码
                doSomethingMore();
                break;*/
        }
    }
    
    private void doSomething() {
        // 其他方法
    }
}
"""
    
    parser = ButterKnifeParser()
    
    # 测试方法边界检测
    method_start, method_end = parser._find_method_boundaries(test_code, "onClick")
    print(f"方法开始位置: {method_start}")
    print(f"方法结束位置: {method_end}")
    
    if method_start != -1 and method_end != -1:
        method_content = test_code[method_start:method_end]
        print(f"方法内容:\n{method_content}")
    
    # 测试参数检测
    has_view_param, param_type = parser._check_method_has_view_param(test_code, "onClick")
    print(f"有View参数: {has_view_param}")
    print(f"参数类型: {param_type}")

if __name__ == "__main__":
    test_method_boundary()
