#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试ButterKnife迁移功能
"""

import os
import tempfile
import shutil
from pathlib import Path

from config import Config
from scanner.file_scanner import FileScanner
from parser.butterknife_parser import ButterKnifeParser
from transformer.findview_transformer import FindViewTransformer
from transformer.onclick_transformer import OnClickTransformer
from transformer.bindcall_remover import BindCallRemover
from injector.code_injector import CodeInjector
from writer.file_writer import FileWriter


def create_test_project():
    """创建测试项目"""
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="butterknife_test_")
    
    # 创建测试Java文件
    test_java_content = '''package com.example.test;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import butterknife.BindView;
import butterknife.ButterKnife;
import butterknife.OnClick;

public class MainActivity extends AppCompatActivity {
    
    @BindView(R.id.title_text)
    TextView titleText;
    
    @BindView(R.id.submit_button)
    Button submitButton;
    
    @BindView(R.id.cancel_button)
    Button cancelButton;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        ButterKnife.bind(this);
        
        // 其他初始化代码
        titleText.setText("Hello World");
    }
    
    @OnClick({R.id.submit_button, R.id.cancel_button})
    public void onButtonClick(View view) {
        if (view.getId() == R.id.submit_button) {
            // 处理提交按钮点击
            titleText.setText("Submit clicked!");
        } else if (view.getId() == R.id.cancel_button) {
            // 处理取消按钮点击
            titleText.setText("Cancel clicked!");
        }
    }
    
    @OnClick(R.id.title_text)
    public void onTitleClick(View view) {
        // 处理标题点击
        titleText.setText("Title clicked!");
    }
}
'''
    
    # 创建目录结构
    java_dir = Path(temp_dir) / "app" / "src" / "main" / "java" / "com" / "example" / "test"
    java_dir.mkdir(parents=True, exist_ok=True)
    
    # 写入测试文件
    test_file_path = java_dir / "MainActivity.java"
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_java_content)
    
    return temp_dir, str(test_file_path)


def test_migration():
    """测试迁移功能"""
    print("开始测试ButterKnife迁移功能...")
    
    # 创建测试项目
    test_dir, test_file = create_test_project()
    print(f"测试项目已创建: {test_dir}")
    print(f"测试文件: {test_file}")
    
    try:
        # 创建配置
        config = Config()
        config.PROJECT_PATH = test_dir
        config.BACKUP_ENABLED = True
        
        # 1. 测试文件扫描
        print("\n1. 测试文件扫描...")
        scanner = FileScanner(config)
        java_files = scanner.scan_files()
        print(f"扫描到 {len(java_files)} 个Java文件")
        
        # 2. 测试注解解析
        print("\n2. 测试注解解析...")
        parser = ButterKnifeParser()
        
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parsed_data = parser.parse(content)
        print(f"解析结果: {parsed_data['has_butterknife']}")
        print(f"@BindView注解: {len(parsed_data['bind_views'])} 个")
        print(f"@OnClick注解: {len(parsed_data['on_clicks'])} 个")
        print(f"ButterKnife.bind调用: {parsed_data['bind_call']}")
        
        # 3. 测试代码转换
        print("\n3. 测试代码转换...")
        
        # FindView转换
        findview_transformer = FindViewTransformer()
        transformed_content = findview_transformer.transform(parsed_data, content)
        print("FindView转换完成")
        
        # OnClick转换
        onclick_transformer = OnClickTransformer()
        transformed_content = onclick_transformer.transform(parsed_data, transformed_content)
        print("OnClick转换完成")
        
        # BindCall移除
        bindcall_remover = BindCallRemover()
        transformed_content = bindcall_remover.transform(parsed_data, transformed_content)
        print("BindCall移除完成")
        
        # 4. 测试代码注入
        print("\n4. 测试代码注入...")
        injector = CodeInjector()
        final_content = injector.inject(transformed_content, parsed_data)
        print("代码注入完成")
        
        # 5. 测试文件写入
        print("\n5. 测试文件写入...")
        writer = FileWriter(config)
        success = writer.write_file(test_file, final_content)
        print(f"文件写入: {'成功' if success else '失败'}")
        
        # 6. 显示转换结果
        print("\n6. 转换结果预览:")
        print("=" * 50)
        
        # 读取转换后的文件
        with open(test_file, 'r', encoding='utf-8') as f:
            final_content = f.read()
        
        # 显示关键部分
        lines = final_content.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in ['findViewById', 'setOnClickListener', 'initializeViews']):
                print(f"{i+1:3d}: {line}")
        
        print("=" * 50)
        
        # 7. 显示迁移报告
        print("\n7. 迁移报告:")
        writer.print_migration_summary()
        
        print("\n测试完成!")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试文件
        print(f"\n清理测试文件: {test_dir}")
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == '__main__':
    test_migration()
