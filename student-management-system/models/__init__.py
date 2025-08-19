#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型模块初始化
Database Models Module
"""

from flask_sqlalchemy import SQLAlchemy

# 创建数据库实例
db = SQLAlchemy()

# 导入所有模型
from .student import Student
from .course import Course
from .book import Book
from .enrollment import Enrollment
from .borrow_record import BorrowRecord

__all__ = ['db', 'Student', 'Course', 'Book', 'Enrollment', 'BorrowRecord']
