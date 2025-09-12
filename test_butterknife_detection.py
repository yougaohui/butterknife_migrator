#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

from butterknife_parser_module.butterknife_parser import ButterKnifeParser

# 测试ButterKnife检测
parser = ButterKnifeParser()

# 读取测试文件
with open('tests/Agent_DeviceListActivity.java', 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否包含ButterKnife相关字符串
print("检查@BindView:", '@BindView' in content)
print("检查@OnClick:", '@OnClick' in content)
print("检查ButterKnife.bind:", 'ButterKnife.bind' in content)
print("检查import butterknife:", 'import butterknife' in content)

# 检测ButterKnife注解
has_butterknife = parser._has_butterknife_annotations(content)
print(f"检测到ButterKnife注解: {has_butterknife}")

# 解析ButterKnife注解
if has_butterknife:
    parsed_data = parser.parse(content)
    print(f"解析结果: {parsed_data}")
else:
    print("未检测到ButterKnife注解")
