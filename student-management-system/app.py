#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生信息管理系统 - 主应用文件
Student Information Management System - Main Application

作者: Assistant
创建时间: 2025-08-15
"""

import os
import argparse
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# 导入配置
from config import Config
from models import db
from api import api_bp
from views import main_bp

def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    Migrate(app, db)
    CORS(app)
    
    # 注册蓝图
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(main_bp)
    
    # 主页路由
    @app.route('/')
    def index():
        return redirect(url_for('main.dashboard'))
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app

def init_database(app):
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 创建示例数据
        from models.student import Student
        from models.course import Course
        from models.book import Book
        
        # 检查是否已有数据
        if Student.query.first() is None:
            # 创建示例学生
            students = [
                Student(
                    student_id='2023001001',
                    name='张三',
                    id_card='110101200001011234',
                    gender='男',
                    age=22,
                    major='计算机科学与技术',
                    grade='2023',
                    email='zhangsan@example.com',
                    phone='13800138001'
                ),
                Student(
                    student_id='2023001002',
                    name='李四',
                    id_card='110101200002021235',
                    gender='女',
                    age=21,
                    major='软件工程',
                    grade='2023',
                    email='lisi@example.com',
                    phone='13800138002'
                )
            ]
            
            # 创建示例课程
            courses = [
                Course(code='CS101', name='计算机程序设计基础', credits=3, teacher='王教授', semester='2024春'),
                Course(code='CS102', name='数据结构与算法', credits=4, teacher='李教授', semester='2024春'),
                Course(code='CS103', name='数据库系统原理', credits=3, teacher='张教授', semester='2024春')
            ]
            
            # 创建示例图书
            books = [
                Book(isbn='9787302123456', title='Python编程：从入门到实践', author='埃里克·马瑟斯', publisher='人民邮电出版社', total_copies=5),
                Book(isbn='9787111123457', title='算法导论', author='托马斯·科尔曼', publisher='机械工业出版社', total_copies=3),
                Book(isbn='9787115123458', title='数据库系统概念', author='亚伯拉罕·西尔伯沙茨', publisher='人民邮电出版社', total_copies=4)
            ]
            
            # 添加到数据库
            for student in students:
                db.session.add(student)
            for course in courses:
                db.session.add(course)
            for book in books:
                db.session.add(book)
            
            db.session.commit()
            print("数据库初始化完成！")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='学生信息管理系统')
    parser.add_argument('--port', type=int, default=5000, help='服务器端口')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    parser.add_argument('--init-db', action='store_true', help='初始化数据库')
    args = parser.parse_args()
    
    app = create_app()
    
    if args.init_db:
        init_database(app)
    
    print(f"🚀 学生信息管理系统启动中...")
    print(f"📊 管理后台将在 http://localhost:{args.port} 启动")
    print(f"🔧 API接口地址: http://localhost:{args.port}/api")
    
    app.run(host='0.0.0.0', port=args.port, debug=args.debug)
