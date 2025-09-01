#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统完整性检查脚本
System Integrity Check Script
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_imports():
    """检查关键模块导入"""
    print("🔍 检查模块导入...")
    
    try:
        import flask
        print(f"  ✅ Flask: {flask.__version__}")
    except ImportError as e:
        print(f"  ❌ Flask导入失败: {e}")
        return False
    
    try:
        from flask_sqlalchemy import SQLAlchemy
        print("  ✅ Flask-SQLAlchemy: 已安装")
    except ImportError as e:
        print(f"  ❌ Flask-SQLAlchemy导入失败: {e}")
        return False
    
    try:
        from config import Config
        print("  ✅ 配置模块: 正常")
    except ImportError as e:
        print(f"  ❌ 配置模块导入失败: {e}")
        return False
    
    return True

def check_models():
    """检查模型定义"""
    print("\n📋 检查模型定义...")
    
    try:
        from models import db, Student, Course, Book, Enrollment, BorrowRecord
        print("  ✅ 所有模型导入成功")
        
        # 检查模型属性
        required_attrs = {
            'Student': ['student_id', 'name', 'id_card', 'gender', 'age'],
            'Course': ['code', 'name', 'credits', 'teacher', 'semester'],
            'Book': ['isbn', 'title', 'author', 'publisher', 'total_copies'],
            'Enrollment': ['student_id', 'course_id', 'status'],
            'BorrowRecord': ['student_id', 'book_id', 'borrow_date', 'due_date', 'status']
        }
        
        models = {
            'Student': Student,
            'Course': Course,
            'Book': Book,
            'Enrollment': Enrollment,
            'BorrowRecord': BorrowRecord
        }
        
        for model_name, model_class in models.items():
            attrs = required_attrs[model_name]
            for attr in attrs:
                if hasattr(model_class, attr):
                    print(f"    ✅ {model_name}.{attr}")
                else:
                    print(f"    ❌ {model_name}.{attr} 缺失")
                    return False
        
        return True
        
    except ImportError as e:
        print(f"  ❌ 模型导入失败: {e}")
        return False

def check_api():
    """检查API模块"""
    print("\n🌐 检查API模块...")
    
    try:
        from api import api_bp
        print("  ✅ API蓝图导入成功")
        
        # 检查具体的API模块
        api_modules = [
            'api.students',
            'api.courses', 
            'api.books',
            'api.enrollments',
            'api.borrows',
            'api.dashboard'
        ]
        
        for module_name in api_modules:
            try:
                __import__(module_name)
                print(f"    ✅ {module_name}")
            except ImportError as e:
                print(f"    ❌ {module_name} 导入失败: {e}")
                return False
        
        return True
        
    except ImportError as e:
        print(f"  ❌ API模块导入失败: {e}")
        return False

def check_views():
    """检查视图模块"""
    print("\n🖼️  检查视图模块...")
    
    try:
        from views import main_bp
        print("  ✅ 视图蓝图导入成功")
        
        # 检查具体的视图模块
        view_modules = [
            'views.dashboard',
            'views.students',
            'views.courses',
            'views.books',
            'views.enrollments',
            'views.borrows'
        ]
        
        for module_name in view_modules:
            try:
                __import__(module_name)
                print(f"    ✅ {module_name}")
            except ImportError as e:
                print(f"    ❌ {module_name} 导入失败: {e}")
                return False
        
        return True
        
    except ImportError as e:
        print(f"  ❌ 视图模块导入失败: {e}")
        return False

def check_templates():
    """检查模板文件"""
    print("\n📄 检查模板文件...")
    
    required_templates = [
        'templates/base.html',
        'templates/dashboard.html',
        'templates/errors/404.html',
        'templates/errors/500.html',
        'templates/students/',
        'templates/courses/',
        'templates/books/',
        'templates/enrollments/',
        'templates/borrows/'
    ]
    
    all_exists = True
    for template in required_templates:
        if os.path.exists(template):
            print(f"    ✅ {template}")
        else:
            print(f"    ❌ {template} 不存在")
            all_exists = False
    
    return all_exists

def check_static_files():
    """检查静态文件"""
    print("\n🎨 检查静态文件...")
    
    static_dirs = [
        'static/css/',
        'static/js/'
    ]
    
    all_exists = True
    for static_dir in static_dirs:
        if os.path.exists(static_dir):
            print(f"    ✅ {static_dir}")
        else:
            print(f"    ❌ {static_dir} 不存在")
            all_exists = False
    
    return all_exists

def check_app_creation():
    """检查应用创建"""
    print("\n🚀 检查应用创建...")
    
    try:
        from app import create_app
        from config import TestingConfig
        
        app = create_app(TestingConfig)
        print("  ✅ 应用创建成功")
        
        # 检查路由数量
        routes_count = len(list(app.url_map.iter_rules()))
        print(f"  ✅ 路由数量: {routes_count}")
        
        if routes_count > 20:  # 应该有足够的路由
            print("  ✅ 路由数量正常")
        else:
            print("  ⚠️  路由数量偏少，可能有问题")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 应用创建失败: {e}")
        return False

def main():
    """主检查函数"""
    print("="*60)
    print("🎯 学生管理系统 - 系统完整性检查")
    print("="*60)
    
    checks = [
        ("模块导入", check_imports),
        ("模型定义", check_models),
        ("API模块", check_api),
        ("视图模块", check_views),
        ("模板文件", check_templates),
        ("静态文件", check_static_files),
        ("应用创建", check_app_creation)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        try:
            if check_func():
                passed += 1
                print(f"\n✅ {name}: 通过")
            else:
                print(f"\n❌ {name}: 失败")
        except Exception as e:
            print(f"\n❌ {name}: 异常 - {e}")
    
    print("\n" + "="*60)
    print(f"📊 检查结果: {passed}/{total} 项通过")
    
    if passed == total:
        print("🎉 系统完整性检查全部通过！")
        print("✅ 系统已准备就绪，可以启动服务")
        return True
    else:
        print("⚠️  系统存在问题，需要修复后再启动")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
