#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest配置文件
Pytest Configuration
"""

import pytest
import tempfile
import os
from app import create_app
from models import db
from config import TestingConfig

@pytest.fixture
def app():
    """创建测试应用实例"""
    # 创建临时数据库文件
    db_fd, db_path = tempfile.mkstemp()
    
    # 配置测试应用
    class TestConfig(TestingConfig):
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    # 清理临时文件
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """创建测试运行器"""
    return app.test_cli_runner()

@pytest.fixture
def sample_student():
    """创建示例学生数据"""
    return {
        'student_id': 'TEST001',
        'name': '测试学生',
        'id_card': '110101200001011234',
        'gender': '男',
        'age': 22,
        'major': '计算机科学与技术',
        'grade': '2023',
        'email': 'test@example.com',
        'phone': '13800138000'
    }

@pytest.fixture
def sample_course():
    """创建示例课程数据"""
    return {
        'code': 'TEST101',
        'name': '测试课程',
        'credits': 3,
        'teacher': '测试教师',
        'semester': '2024春'
    }

@pytest.fixture
def sample_book():
    """创建示例图书数据"""
    return {
        'isbn': '9787302000000',
        'title': '测试图书',
        'author': '测试作者',
        'publisher': '测试出版社',
        'total_copies': 3
    }
