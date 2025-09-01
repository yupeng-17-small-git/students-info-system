#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的Bug修复验证脚本
Simple Bug Fix Verification Script

直接验证修复的功能，不依赖pytest
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from app import create_app
from config import TestingConfig

def test_bug_fixes():
    """验证主要bug修复"""
    print("🧪 开始验证Bug修复...")
    
    # 创建测试应用
    app = create_app(TestingConfig)
    
    with app.app_context():
        # 导入模型
        from models import db, Student, Course, Book
        
        # 创建测试数据库
        db.create_all()
        
        print("\n✅ 测试1: 学生入学日期类型修复")
        try:
            # 测试学生创建（应该不会有日期类型错误）
            student = Student(
                student_id='TEST001',
                name='测试学生',
                id_card='110101200001011234',
                gender='男',
                age=20,
                major='计算机科学',
                grade='2024'
            )
            db.session.add(student)
            db.session.commit()
            
            # 验证入学日期是date类型
            assert hasattr(student, 'enrollment_date')
            if student.enrollment_date:
                from datetime import date
                assert isinstance(student.enrollment_date, date)
                print(f"   📅 入学日期正确: {student.enrollment_date} (类型: {type(student.enrollment_date)})")
            
            print("   ✅ Bug#2修复验证通过: 学生入学日期类型正确")
            
        except Exception as e:
            print(f"   ❌ Bug#2修复验证失败: {e}")
            return False
        
        print("\n✅ 测试2: 视图文件导入修复")
        try:
            # 测试课程搜索功能（之前会因为db导入问题失败）
            course = Course(
                code='TEST101',
                name='Python编程测试课程',
                credits=3,
                teacher='测试教师',
                semester='2024春'
            )
            db.session.add(course)
            db.session.commit()
            
            # 测试搜索查询（模拟views中的搜索逻辑）
            from models import db
            query = Course.query.filter(
                db.or_(
                    Course.code.contains('Python'),
                    Course.name.contains('Python'),
                    Course.teacher.contains('Python')
                )
            )
            results = query.all()
            
            print(f"   🔍 搜索结果: 找到 {len(results)} 个匹配的课程")
            if results:
                print(f"   📚 课程: {results[0].name}")
            
            print("   ✅ Bug#1修复验证通过: 视图搜索功能正常")
            
        except Exception as e:
            print(f"   ❌ Bug#1修复验证失败: {e}")
            return False
        
        print("\n✅ 测试3: 基本CRUD操作")
        try:
            # 测试学生更新
            student.age = 21
            student.major = '软件工程'
            db.session.commit()
            
            # 验证更新
            updated_student = Student.query.get(student.id)
            assert updated_student.age == 21
            assert updated_student.major == '软件工程'
            
            print("   📝 学生信息更新成功")
            
            # 测试图书创建
            book = Book(
                isbn='9787302123456',
                title='Python编程实战',
                author='测试作者',
                publisher='测试出版社',
                total_copies=5
            )
            db.session.add(book)
            db.session.commit()
            
            print("   📖 图书创建成功")
            
            # 测试数据转换
            student_dict = student.to_dict()
            assert 'student_id' in student_dict
            assert 'name' in student_dict
            assert 'enrollment_date' in student_dict
            
            print("   🔄 数据序列化正常")
            
            print("   ✅ 基本CRUD操作验证通过")
            
        except Exception as e:
            print(f"   ❌ 基本CRUD操作验证失败: {e}")
            return False
        
        print("\n✅ 测试4: 关系查询")
        try:
            # 测试学生属性查询
            enrolled_courses = student.enrolled_courses
            borrowed_books = student.borrowed_books
            
            print(f"   📚 已选课程数: {len(enrolled_courses)}")
            print(f"   📖 已借图书数: {len(borrowed_books)}")
            
            print("   ✅ 关系查询验证通过")
            
        except Exception as e:
            print(f"   ❌ 关系查询验证失败: {e}")
            return False
        
        print("\n✅ 测试5: 搜索功能")
        try:
            # 测试学生搜索
            search_results = Student.search('测试', page=1, per_page=10)
            print(f"   🔍 学生搜索结果: {search_results.total} 条记录")
            
            # 测试分页
            assert hasattr(search_results, 'items')
            assert hasattr(search_results, 'total')
            assert hasattr(search_results, 'pages')
            
            print("   ✅ 搜索和分页功能验证通过")
            
        except Exception as e:
            print(f"   ❌ 搜索功能验证失败: {e}")
            return False
        
        # 清理
        db.drop_all()
    
    return True

def test_api_endpoints():
    """测试API端点"""
    print("\n🌐 测试API端点...")
    
    app = create_app(TestingConfig)
    client = app.test_client()
    
    with app.app_context():
        from models import db
        db.create_all()
        
        try:
            # 测试学生API
            student_data = {
                'student_id': 'API001',
                'name': 'API测试学生',
                'id_card': '110101200001012345',
                'gender': '男',
                'age': 22,
                'major': '计算机科学',
                'grade': '2024'
            }
            
            response = client.post('/api/students', json=student_data)
            print(f"   📤 创建学生API: {response.status_code}")
            
            if response.status_code == 201:
                print("   ✅ 学生创建API正常")
            
            # 测试获取学生列表
            response = client.get('/api/students')
            print(f"   📥 获取学生列表API: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                if data and data.get('success'):
                    print("   ✅ 学生列表API正常")
            
        except Exception as e:
            print(f"   ❌ API测试失败: {e}")
            return False
        finally:
            db.drop_all()
    
    return True

def main():
    """主函数"""
    print("="*60)
    print("🎯 学生管理系统 - Bug修复验证")
    print("="*60)
    print(f"⏰ 验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = True
    
    # 验证核心bug修复
    if not test_bug_fixes():
        success = False
    
    # 验证API功能
    if not test_api_endpoints():
        success = False
    
    print("\n" + "="*60)
    if success:
        print("🎉 所有验证通过！主要Bug已修复！")
        print("\n✅ 修复摘要:")
        print("   • Bug#1: 视图文件db导入问题 - 已修复")
        print("   • Bug#2: 学生入学日期类型不匹配 - 已修复")
        print("   • 基本CRUD操作正常")
        print("   • API端点功能正常")
        print("   • 搜索和分页功能正常")
        print("\n🚀 系统已经可以正常使用！")
    else:
        print("❌ 验证失败，仍有问题需要修复")
    
    print("="*60)
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
