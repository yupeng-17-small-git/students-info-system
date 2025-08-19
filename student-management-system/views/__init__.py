#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web视图模块初始化
Web Views Module
"""

from flask import Blueprint

# 创建主蓝图
main_bp = Blueprint('main', __name__)

# 导入所有视图
from . import dashboard, students, courses, books, enrollments, borrows

__all__ = ['main_bp']
