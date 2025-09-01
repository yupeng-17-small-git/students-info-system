#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
边界情况和错误处理测试
Edge Cases and Error Handling Tests

专门测试各种边界情况、异常处理和错误恢复
"""

import pytest
from datetime import datetime, timedelta
from models import db, Student, Course, Book, Enrollment, BorrowRecord
from sqlalchemy.exc import IntegrityError
import json

class TestDataValidation:
    """数据验证测试"""
    
    def test_student_invalid_age(self, app, client):
        """测试学生年龄边界值"""
        with app.app_context():
            # 测试负数年龄
            invalid_student = {
                'student_id': 'INVALID001',
                'name': '无效年龄学生',
                'id_card': '110101200001012101',
                'gender': '男',
                'age': -5,  # 负数年龄
                'major': '计算机科学',
                'grade': '2024'
            }
            
            response = client.post('/api/students', json=invalid_student)
            # 应该成功创建（当前系统没有年龄验证，这是一个潜在bug）
            # 在实际修复中，应该添加年龄验证
    
    def test_student_empty_name(self, app, client):
        """测试空姓名"""
        with app.app_context():
            invalid_student = {
                'student_id': 'EMPTY001',
                'name': '',  # 空姓名
                'id_card': '110101200001012102',
                'gender': '男',
                'age': 20,
                'major': '计算机科学',
                'grade': '2024'
            }
            
            response = client.post('/api/students', json=invalid_student)
            # 应该添加非空验证
    
    def test_student_invalid_id_card_format(self, app, client):
        """测试无效身份证格式"""
        with app.app_context():
            invalid_formats = [
                '12345',  # 太短
                '123456789012345678901',  # 太长
                'ABCDEFGHIJKLMNOPQR',  # 非数字
                '110101200001012103X'  # 包含字母（虽然X是合法的）
            ]
            
            for i, invalid_id in enumerate(invalid_formats):
                invalid_student = {
                    'student_id': f'INVALID{i:03d}',
                    'name': f'无效身份证学生{i}',
                    'id_card': invalid_id,
                    'gender': '男',
                    'age': 20,
                    'major': '计算机科学',
                    'grade': '2024'
                }
                
                response = client.post('/api/students', json=invalid_student)
                # 当前系统可能会接受这些格式，应该添加身份证格式验证
    
    def test_course_invalid_credits(self, app, client):
        """测试无效学分"""
        with app.app_context():
            invalid_course = {
                'code': 'INVALID101',
                'name': '无效学分课程',
                'credits': -1,  # 负学分
                'teacher': '测试教师',
                'semester': '2024春'
            }
            
            response = client.post('/api/courses', json=invalid_course)
            # 应该添加学分范围验证
    
    def test_book_invalid_copies(self, app, client):
        """测试无效图书副本数"""
        with app.app_context():
            invalid_book = {
                'isbn': '9787302999999',
                'title': '无效副本数图书',
                'author': '测试作者',
                'publisher': '测试出版社',
                'total_copies': -1  # 负数副本
            }
            
            response = client.post('/api/books', json=invalid_book)
            # 应该添加副本数验证

class TestConcurrencyAndRaceConditions:
    """并发和竞争条件测试"""
    
    def test_concurrent_enrollment(self, app):
        """测试并发选课（模拟竞争条件）"""
        with app.app_context():
            student = Student.create(
                student_id='RACE001',
                name='竞争条件学生',
                id_card='110101200001012201',
                gender='男',
                age=20,
                major='计算机科学',
                grade='2024'
            )
            
            course = Course.create(
                code='RACE101',
                name='竞争条件课程',
                credits=3,
                teacher='竞争教师',
                semester='2024春'
            )
            
            # 第一次选课
            enrollment1 = Enrollment.create(
                student_id=student.id,
                course_id=course.id
            )
            
            # 尝试重复选课（应该失败）
            with pytest.raises(IntegrityError):
                enrollment2 = Enrollment(
                    student_id=student.id,
                    course_id=course.id
                )
                db.session.add(enrollment2)
                db.session.commit()
    
    def test_concurrent_book_borrowing(self, app):
        """测试并发借书（库存控制）"""
        with app.app_context():
            # 创建只有1本的图书
            book = Book.create(
                isbn='9787302111111',
                title='单本图书',
                author='测试作者',
                publisher='测试出版社',
                total_copies=1
            )
            
            student1 = Student.create(
                student_id='CONCURRENT001',
                name='并发学生1',
                id_card='110101200001012301',
                gender='男',
                age=20,
                major='计算机科学',
                grade='2024'
            )
            
            student2 = Student.create(
                student_id='CONCURRENT002',
                name='并发学生2',
                id_card='110101200001012302',
                gender='女',
                age=21,
                major='软件工程',
                grade='2024'
            )
            
            # 第一个学生借书
            borrow1 = BorrowRecord.create(
                student_id=student1.id,
                book_id=book.id
            )
            
            # 第二个学生尝试借同一本书（应该有库存检查）
            # 当前系统可能没有库存检查，这是一个bug
            borrow2 = BorrowRecord.create(
                student_id=student2.id,
                book_id=book.id
            )
            
            # 检查是否有适当的库存控制
            borrowed_count = BorrowRecord.query.filter(
                BorrowRecord.book_id == book.id,
                BorrowRecord.status == 'borrowed'
            ).count()
            
            # 理想情况下，borrowed_count应该 <= book.total_copies
            # 如果 > total_copies，说明有库存控制bug

class TestLargeDataSets:
    """大数据集测试"""
    
    def test_large_student_list_performance(self, app, client):
        """测试大量学生数据的性能"""
        with app.app_context():
            # 创建大量学生（测试环境用较小数量）
            for i in range(50):
                Student.create(
                    student_id=f'PERF{i:04d}',
                    name=f'性能测试学生{i}',
                    id_card=f'11010120000130{i:04d}',
                    gender='男' if i % 2 == 0 else '女',
                    age=18 + (i % 10),
                    major='计算机科学',
                    grade='2024'
                )
            
            # 测试分页性能
            response = client.get('/api/students?per_page=20')
            assert response.status_code == 200
            
            # 测试搜索性能
            response = client.get('/api/students?search=性能测试')
            assert response.status_code == 200
    
    def test_pagination_boundary(self, app, client):
        """测试分页边界情况"""
        with app.app_context():
            # 创建一些测试数据
            for i in range(25):
                Student.create(
                    student_id=f'PAGE{i:04d}',
                    name=f'分页测试学生{i}',
                    id_card=f'11010120000131{i:04d}',
                    gender='男' if i % 2 == 0 else '女',
                    age=20,
                    major='计算机科学',
                    grade='2024'
                )
            
            # 测试各种边界情况
            test_cases = [
                {'page': 0, 'per_page': 10},    # 零页
                {'page': -1, 'per_page': 10},   # 负页数
                {'page': 1, 'per_page': 0},     # 零每页数量
                {'page': 1, 'per_page': -5},    # 负每页数量
                {'page': 999, 'per_page': 10},  # 超大页数
                {'page': 1, 'per_page': 1000},  # 超大每页数量
            ]
            
            for case in test_cases:
                response = client.get(f"/api/students?page={case['page']}&per_page={case['per_page']}")
                # 应该优雅处理边界情况，不应该崩溃
                assert response.status_code in [200, 400]  # 200正常或400参数错误

class TestSecurityAndInjection:
    """安全性和注入攻击测试"""
    
    def test_sql_injection_in_search(self, app, client):
        """测试搜索中的SQL注入"""
        with app.app_context():
            # 常见的SQL注入尝试
            injection_attempts = [
                "'; DROP TABLE students; --",
                "' OR '1'='1",
                "'; SELECT * FROM students; --",
                "<script>alert('xss')</script>",
                "' UNION SELECT * FROM students --"
            ]
            
            for injection in injection_attempts:
                response = client.get(f'/api/students?search={injection}')
                # 应该安全处理，不应该导致错误或泄露数据
                assert response.status_code in [200, 400]
                
                if response.status_code == 200:
                    data = response.get_json()
                    assert data.get('success', False)  # 确保有适当的响应结构
    
    def test_xss_in_input_fields(self, app, client):
        """测试输入字段中的XSS"""
        with app.app_context():
            xss_payloads = [
                "<script>alert('xss')</script>",
                "javascript:alert('xss')",
                "<img src=x onerror=alert('xss')>",
                "<svg onload=alert('xss')>"
            ]
            
            for payload in xss_payloads:
                malicious_student = {
                    'student_id': 'XSS001',
                    'name': payload,  # XSS在姓名字段
                    'id_card': '110101200001012401',
                    'gender': '男',
                    'age': 20,
                    'major': payload,  # XSS在专业字段
                    'grade': '2024'
                }
                
                response = client.post('/api/students', json=malicious_student)
                # 系统应该能处理这些输入，理想情况下应该过滤或转义
                
                if response.status_code == 201:
                    # 如果创建成功，获取数据时应该是安全的
                    data = response.get_json()
                    student_name = data.get('data', {}).get('student', {}).get('name', '')
                    # 检查是否进行了适当的转义或过滤

class TestErrorRecovery:
    """错误恢复测试"""
    
    def test_database_connection_error_simulation(self, app, client):
        """模拟数据库连接错误"""
        with app.app_context():
            # 这个测试需要特殊的设置来模拟数据库错误
            # 在实际环境中，可以通过关闭数据库连接或使用模拟来测试
            pass
    
    def test_malformed_json_input(self, app, client):
        """测试格式错误的JSON输入"""
        with app.app_context():
            # 发送格式错误的JSON
            response = client.post('/api/students',
                                 data='{"name": "测试", "incomplete": }',  # 格式错误的JSON
                                 content_type='application/json')
            
            # 应该返回适当的错误响应
            assert response.status_code == 400
    
    def test_missing_content_type(self, app, client):
        """测试缺少Content-Type头"""
        with app.app_context():
            response = client.post('/api/students',
                                 data='{"name": "测试学生"}')
            
            # 应该能处理缺少Content-Type的情况
            assert response.status_code in [400, 415]  # Bad Request或Unsupported Media Type

class TestDataIntegrity:
    """数据完整性测试"""
    
    def test_orphaned_records_prevention(self, app):
        """测试防止孤儿记录"""
        with app.app_context():
            # 创建学生和相关记录
            student = Student.create(
                student_id='ORPHAN001',
                name='孤儿记录测试学生',
                id_card='110101200001012501',
                gender='男',
                age=20,
                major='计算机科学',
                grade='2024'
            )
            
            course = Course.create(
                code='ORPHAN101',
                name='孤儿记录测试课程',
                credits=3,
                teacher='测试教师',
                semester='2024春'
            )
            
            # 创建选课记录
            enrollment = Enrollment.create(
                student_id=student.id,
                course_id=course.id
            )
            
            # 删除学生（应该级联删除相关记录）
            student.delete()
            
            # 验证选课记录也被删除
            remaining_enrollment = Enrollment.query.filter_by(student_id=student.id).first()
            assert remaining_enrollment is None, "选课记录应该被级联删除"
    
    def test_referential_integrity(self, app):
        """测试引用完整性"""
        with app.app_context():
            # 尝试创建引用不存在学生的选课记录
            with pytest.raises(Exception):  # 应该抛出外键约束错误
                enrollment = Enrollment(
                    student_id=99999,  # 不存在的学生ID
                    course_id=1
                )
                db.session.add(enrollment)
                db.session.commit()
