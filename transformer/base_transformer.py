#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
转换器基类
所有 Transformer 继承自 BaseTransformer，实现统一接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTransformer(ABC):
    """转换器基类"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.description = "基础转换器"
    
    @abstractmethod
    def transform(self, parsed_data: Dict[str, Any], original_code: str) -> str:
        """
        转换代码的核心方法
        
        Args:
            parsed_data: 解析后的ButterKnife注解数据
            original_code: 原始Java代码
            
        Returns:
            转换后的Java代码
        """
        raise NotImplementedError
    
    def can_transform(self, parsed_data: Dict[str, Any]) -> bool:
        """
        检查是否可以应用此转换器
        
        Args:
            parsed_data: 解析后的数据
            
        Returns:
            是否可以应用转换
        """
        return True
    
    def get_transformation_info(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取转换信息
        
        Args:
            parsed_data: 解析后的数据
            
        Returns:
            转换信息字典
        """
        return {
            'transformer_name': self.name,
            'description': self.description,
            'can_apply': self.can_transform(parsed_data),
            'changes_count': 0
        }
    
    def validate_input(self, parsed_data: Dict[str, Any], original_code: str) -> bool:
        """
        验证输入数据的有效性
        
        Args:
            parsed_data: 解析后的数据
            original_code: 原始代码
            
        Returns:
            输入是否有效
        """
        if not isinstance(parsed_data, dict):
            return False
        
        if not isinstance(original_code, str):
            return False
        
        if not original_code.strip():
            return False
        
        return True
    
    def pre_process(self, parsed_data: Dict[str, Any], original_code: str) -> tuple:
        """
        预处理输入数据
        
        Args:
            parsed_data: 解析后的数据
            original_code: 原始代码
            
        Returns:
            预处理后的数据元组
        """
        if not self.validate_input(parsed_data, original_code):
            raise ValueError("输入数据无效")
        
        return parsed_data, original_code
    
    def post_process(self, transformed_code: str) -> str:
        """
        后处理转换后的代码
        
        Args:
            transformed_code: 转换后的代码
            
        Returns:
            后处理后的代码
        """
        # 默认不做后处理，子类可以重写
        return transformed_code
    
    def transform_with_validation(self, parsed_data: Dict[str, Any], original_code: str) -> str:
        """
        带验证的转换方法
        
        Args:
            parsed_data: 解析后的数据
            original_code: 原始代码
            
        Returns:
            转换后的代码
        """
        try:
            # 预处理
            parsed_data, original_code = self.pre_process(parsed_data, original_code)
            
            # 检查是否可以转换
            if not self.can_transform(parsed_data):
                return original_code
            
            # 执行转换
            transformed_code = self.transform(parsed_data, original_code)
            
            # 后处理
            final_code = self.post_process(transformed_code)
            
            return final_code
            
        except Exception as e:
            print(f"转换器 {self.name} 执行失败: {e}")
            return original_code
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        """表示"""
        return f"<{self.name}>"


class TransformerRegistry:
    """转换器注册表"""
    
    def __init__(self):
        self._transformers = {}
    
    def register(self, name: str, transformer: BaseTransformer):
        """注册转换器"""
        self._transformers[name] = transformer
    
    def get(self, name: str) -> BaseTransformer:
        """获取转换器"""
        return self._transformers.get(name)
    
    def get_all(self) -> Dict[str, BaseTransformer]:
        """获取所有转换器"""
        return self._transformers.copy()
    
    def apply_all(self, parsed_data: Dict[str, Any], original_code: str) -> str:
        """应用所有转换器"""
        result = original_code
        
        for name, transformer in self._transformers.items():
            try:
                result = transformer.transform_with_validation(parsed_data, result)
            except Exception as e:
                print(f"应用转换器 {name} 时出错: {e}")
        
        return result
