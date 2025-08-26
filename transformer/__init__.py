#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
转换器模块
每个类负责一种转换逻辑，便于扩展和替换
"""

from .base_transformer import BaseTransformer
from .findview_transformer import FindViewTransformer
from .onclick_transformer import OnClickTransformer
from .bindcall_remover import BindCallRemover

__all__ = [
    'BaseTransformer',
    'FindViewTransformer', 
    'OnClickTransformer',
    'BindCallRemover'
]
