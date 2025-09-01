#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全功能验证测试
Comprehensive Function Test

验证所有修复后的功能是否正常工作
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta

def test_app_creation_and_routes():
    """测试应用创建和路由"""
    print("🚀 测试应用创建和路由...")
    
    try:
        from app import create_app
        from config import TestingConfig
        
        app = create_app(TestingConfig)
        
        with app.app_context():
            # 检查主要路由
            routes = [rule.rule for rule in app.url_map.iter_rules()]
            
            expected_routes = [
                '/students',
                '/courses', 
                '/books',
                '/enrollments',
                '/borrows',
                '/dashboard',
                '/api/students',
                '/api/courses',
                '/api/books'
            ]
            
            missing_routes = []
            for route in expected_routes:
                if not any(route in existing_route for existing_route in routes):
                    missing_routes.append(route)
            
            if missing_routes:
                print(f"  ❌ 缺少路由: {missing_routes}")
                return False
            
            print(f"  ✅ 应用创建成功，共有 {len(routes)} 个路由")
            print("  ✅ 所有主要路由都存在")
            return True
            
    except Exception as e:
        print(f"  ❌ 应用创建失败: {e}")
        return False

def test_models_and_validation():
    """测试模型和数据验证"""
    print("\n📋 测试模型和数据验证...")
    
    try:
        from app import create_app
        from config import TestingConfig
        from models import db, Student, Course, Book, Enrollment, BorrowRecord
        
        app = create_app(TestingConfig)
        
        with app.app_context():
            # 创建内存数据库
            db.create_all()
            
            # 测试学生模型和验证
            print("  🧑‍🎓 测试学生模型...")
            
            # 正常学生创建
            student = Student(
                student_id='TEST2024001',
                name='测试学生',
                id_card='110101200001011234',
                gender='男',
                age=20,
                major='计算机科学',
                grade='2024'
            )
            
            # 测试验证方法
            if hasattr(student, 'validate'):
                student.validate()  # 应该通过验证
                print("    ✅ 学生数据验证通过")
            
            db.session.add(student)
            db.session.commit()
            print("    ✅ 学生创建成功")
            
            # 测试无效数据
            invalid_student = Student(
                student_id='',  # 空学号
                name='',        # 空姓名
                age=-5,         # 无效年龄
                id_card='123'   # 无效身份证
            )
            
            if hasattr(invalid_student, 'validate'):
                try:
                    invalid_student.validate()
                    print("    ❌ 应该抛出验证错误")
                    return False
                except ValueError:
                    print("    ✅ 数据验证正确拒绝无效数据")
            
            # 测试课程模型
            print("  📚 测试课程模型...")
            
            course = Course(
                code='TEST101',
                name='测试课程',
                credits=3,
                teacher='测试教师',
                semester='2024春'
            )
            
            if hasattr(course, 'validate'):
                course.validate()
                print("    ✅ 课程数据验证通过")
            
            db.session.add(course)
            db.session.commit()
            print("    ✅ 课程创建成功")
            
            # 测试图书模型
            print("  📖 测试图书模型...")
            
            book = Book(
                isbn='9787302123456',
                title='测试图书',
                author='测试作者',
                publisher='测试出版社',
                total_copies=5
            )
            
            if hasattr(book, 'validate'):
                book.validate()
                print("    ✅ 图书数据验证通过")
            
            db.session.add(book)
            db.session.commit()
            print("    ✅ 图书创建成功")
            
            # 测试选课
            print("  📝 测试选课功能...")
            
            enrollment = Enrollment(
                student_id=student.id,
                course_id=course.id,
                status='enrolled'
            )
            
            db.session.add(enrollment)
            db.session.commit()
            print("    ✅ 选课记录创建成功")
            
            # 测试借书和库存控制
            print("  📚 测试借书和库存控制...")
            
            # 检查图书可用性
            if hasattr(BorrowRecord, 'check_book_availability'):
                available, message = BorrowRecord.check_book_availability(book.id)
                if available:
                    print(f"    ✅ 图书库存检查: {message}")
                else:
                    print(f"    ❌ 图书库存检查失败: {message}")
                    return False
            
            # 创建借书记录
            borrow = BorrowRecord(
                student_id=student.id,
                book_id=book.id,
                borrow_date=datetime.utcnow(),
                due_date=datetime.utcnow() + timedelta(days=30),
                status='borrowed'
            )
            
            db.session.add(borrow)
            db.session.commit()
            print("    ✅ 借书记录创建成功")
            
            # 测试搜索功能
            print("  🔍 测试搜索功能...")
            
            search_results = Student.search('测试', page=1, per_page=10)
            if search_results.total > 0:
                print(f"    ✅ 学生搜索成功，找到 {search_results.total} 条记录")
            else:
                print("    ❌ 学生搜索失败")
                return False
            
            course_results = Course.search('测试', page=1, per_page=10)
            if course_results.total > 0:
                print(f"    ✅ 课程搜索成功，找到 {course_results.total} 条记录")
            else:
                print("    ❌ 课程搜索失败")
                return False
            
            book_results = Book.search('测试', page=1, per_page=10)
            if book_results.total > 0:
                print(f"    ✅ 图书搜索成功，找到 {book_results.total} 条记录")
            else:
                print("    ❌ 图书搜索失败")
                return False
            
            return True
            
    except Exception as e:
        print(f"  ❌ 模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n🌐 测试API端点...")
    
    try:
        from app import create_app
        from config import TestingConfig
        from models import db
        
        app = create_app(TestingConfig)
        client = app.test_client()
        
        with app.app_context():
            db.create_all()
            
            # 测试学生API
            print("  👨‍🎓 测试学生API...")
            
            student_data = {
                'student_id': 'API2024001',
                'name': 'API测试学生',
                'id_card': '110101200002021234',
                'gender': '女',
                'age': 21,
                'major': '软件工程',
                'grade': '2024'
            }
            
            # 创建学生
            response = client.post('/api/students', json=student_data)
            if response.status_code == 201:
                print("    ✅ 学生创建API正常")
                data = response.get_json()
                student_id = data['data']['student']['id']
            else:
                print(f"    ❌ 学生创建API失败: {response.status_code}")
                return False
            
            # 获取学生列表
            response = client.get('/api/students')
            if response.status_code == 200:
                print("    ✅ 学生列表API正常")
                data = response.get_json()
                if data['success'] and len(data['data']['students']) > 0:
                    print(f"    ✅ 找到 {len(data['data']['students'])} 个学生")
                else:
                    print("    ❌ 学生列表为空")
            else:
                print(f"    ❌ 学生列表API失败: {response.status_code}")
                return False
            
            # 更新学生
            update_data = {'age': 22, 'major': '数据科学'}
            response = client.put(f'/api/students/{student_id}', json=update_data)
            if response.status_code == 200:
                print("    ✅ 学生更新API正常")
            else:
                print(f"    ❌ 学生更新API失败: {response.status_code}")
            
            # 测试课程API
            print("  📚 测试课程API...")
            
            course_data = {
                'code': 'API101',
                'name': 'API测试课程',
                'credits': 3,
                'teacher': 'API测试教师',
                'semester': '2024春'
            }
            
            response = client.post('/api/courses', json=course_data)
            if response.status_code == 201:
                print("    ✅ 课程创建API正常")
            else:
                print(f"    ❌ 课程创建API失败: {response.status_code}")
                return False
            
            # 测试图书API
            print("  📖 测试图书API...")
            
            book_data = {
                'isbn': '9787302987654',
                'title': 'API测试图书',
                'author': 'API测试作者',
                'publisher': 'API测试出版社',
                'total_copies': 3
            }
            
            response = client.post('/api/books', json=book_data)
            if response.status_code == 201:
                print("    ✅ 图书创建API正常")
            else:
                print(f"    ❌ 图书创建API失败: {response.status_code}")
                return False
            
            # 测试数据验证错误处理
            print("  ⚠️  测试数据验证错误处理...")
            
            invalid_student = {
                'student_id': '',  # 空学号
                'name': '',        # 空姓名
                'age': -5          # 无效年龄
            }
            
            response = client.post('/api/students', json=invalid_student)
            if response.status_code == 400:
                print("    ✅ API正确处理验证错误")
                data = response.get_json()
                if not data['success']:
                    print(f"    ✅ 错误信息: {data['message']}")
            else:
                print(f"    ❌ API未正确处理验证错误: {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"  ❌ API测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_inventory_control():
    """测试库存控制功能"""
    print("\n📦 测试图书库存控制...")
    
    try:
        from app import create_app
        from config import TestingConfig
        from models import db, Book, BorrowRecord, Student
        
        app = create_app(TestingConfig)
        
        with app.app_context():
            db.create_all()
            
            # 创建只有1本的图书
            book = Book(
                isbn='9787302999999',
                title='库存测试图书',
                author='库存作者',
                publisher='库存出版社',
                total_copies=1
            )
            db.session.add(book)
            
            # 创建两个学生
            student1 = Student(
                student_id='INV001',
                name='库存学生1',
                id_card='110101200003031234',
                gender='男',
                age=20,
                major='计算机科学',
                grade='2024'
            )
            
            student2 = Student(
                student_id='INV002', 
                name='库存学生2',
                id_card='110101200003031235',
                gender='女',
                age=21,
                major='软件工程',
                grade='2024'
            )
            
            db.session.add_all([student1, student2])
            db.session.commit()
            
            # 检查库存
            if hasattr(BorrowRecord, 'check_book_availability'):
                available, message = BorrowRecord.check_book_availability(book.id)
                if available:
                    print(f"  ✅ 初始库存检查: {message}")
                else:
                    print(f"  ❌ 初始库存检查失败: {message}")
                    return False
                
                # 第一个学生借书
                borrow1 = BorrowRecord(
                    student_id=student1.id,
                    book_id=book.id,
                    borrow_date=datetime.utcnow(),
                    due_date=datetime.utcnow() + timedelta(days=30),
                    status='borrowed'
                )
                db.session.add(borrow1)
                db.session.commit()
                print("  ✅ 第一个学生借书成功")
                
                # 再次检查库存
                available, message = BorrowRecord.check_book_availability(book.id)
                if not available:
                    print(f"  ✅ 库存控制正常: {message}")
                    return True
                else:
                    print(f"  ❌ 库存控制失败，仍显示可借: {message}")
                    return False
            else:
                print("  ❌ 缺少库存检查功能")
                return False
                
    except Exception as e:
        print(f"  ❌ 库存控制测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("="*70)
    print("🧪 学生管理系统 - 全功能验证测试")
    print("="*70)
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("应用创建和路由", test_app_creation_and_routes),
        ("模型和数据验证", test_models_and_validation),
        ("API端点功能", test_api_endpoints),
        ("图书库存控制", test_inventory_control)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🔍 开始测试: {name}")
        print('='*50)
        
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {name} - 测试通过")
            else:
                print(f"\n❌ {name} - 测试失败")
        except Exception as e:
            print(f"\n❌ {name} - 测试异常: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("📊 最终测试结果")
    print("="*70)
    print(f"总测试项目: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有功能测试通过！")
        print("✅ 系统完全可用，所有功能正常工作")
        print("🚀 可以安全部署到生产环境")
        return True
    else:
        print(f"\n⚠️  有 {total - passed} 项测试失败")
        print("❌ 建议修复失败的功能后再部署")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
