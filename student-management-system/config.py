#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
Configuration settings for the Student Management System
"""

import os
from pathlib import Path

basedir = Path(__file__).parent.absolute()

class Config:
    """基础配置类"""
    # 密钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'student-management-secret-key-2025'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{basedir}/student_management.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # 分页配置
    ITEMS_PER_PAGE = 10
    
    # API配置
    JSON_AS_ASCII = False  # 支持中文
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    # 上传文件配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    
class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    
class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

# 配置字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
