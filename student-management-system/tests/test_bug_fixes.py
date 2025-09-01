#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bug修复测试
Bug Fix Tests

专门测试已发现和修复的bug，确保不会再次出现
"""

import pytest
from datetime import datetime, timedelta, date
from models import db, Student, Course, Book, Enrollment, BorrowRecord
from sqlalchemy.exc import IntegrityError

class TestBugFixes:
    """Bug修复测试类"""
    
    def test_bug_fix_views_db_import(self, app, client):
        """测试Bug#1: 视图文件中缺少db导入的搜索功能"""
        with app.app_context():
            # 创建测试数据
            course = Course.create(
                code='TEST101',
                name='测试课程Python',
                credits=3,
                teacher='测试老师',
                semester='2024春'
            )
            
            book = Book.create(
                isbn='9787302000001',
                title='Python编程测试',
                author='测试作者',
                publisher='测试出版社',
                total_copies=5
            )
            
            # 测试课程搜索（之前会因为db导入问题失败）
            response = client.get('/courses?search=Python')
            assert response.status_code == 200
            
            # 测试图书搜索
            response = client.get('/books?search=Python')
            assert response.status_code == 200
    
    def test_bug_fix_student_enrollment_date_type(self, app):
        """测试Bug#2: 学生入学日期类型不匹配问题"""
        with app.app_context():
            # 创建学生时不指定入学日期，使用默认值
            student = Student.create(
                student_id='TEST2024001',
                name='测试学生',
                id_card='110101200001011111',
                gender='男',
                age=20,
                major='计算机科学',
                grade='2024'
            )
            
            # 验证入学日期是date类型，不是datetime
            assert isinstance(student.enrollment_date, date)
            assert not isinstance(student.enrollment_date, datetime)
            
            # 验证日期是今天
            assert student.enrollment_date == datetime.utcnow().date()
    
    def test_bug_fix_borrow_record_overdue_property(self, app):
        """测试Bug#3: 借书记录逾期判断中的潜在空指针异常"""
        with app.app_context():
            student = Student.create(
                student_id='TEST2024002',
                name='测试学生逾期',
                id_card='110101200001011112',
                gender='女',
                age=21,
                major='软件工程',
                grade='2024'
            )
            
            book = Book.create(
                isbn='9787302000002',
                title='测试图书逾期',
                author='测试作者',
                publisher='测试出版社',
                total_copies=3
            )
            
            # 创建借书记录，但不设置due_date
            borrow_record = BorrowRecord(
                student_id=student.id,
                book_id=book.id,
                borrow_date=datetime.utcnow()
            )
            db.session.add(borrow_record)
            db.session.commit()
            
            # 验证due_date被正确设置（应该是借书日期+30天）
            assert borrow_record.due_date is not None
            expected_due_date = borrow_record.borrow_date + timedelta(days=30)
            assert borrow_record.due_date.date() == expected_due_date.date()
            
            # 测试逾期属性不会抛出异常
            assert not borrow_record.is_overdue  # 新借的书不应该逾期
            assert borrow_record.days_overdue == 0
            
            # 手动设置逾期
            borrow_record.due_date = datetime.utcnow() - timedelta(days=5)
            db.session.commit()
            
            assert borrow_record.is_overdue
            assert borrow_record.days_overdue == 5
    
    def test_bug_fix_api_error_handling(self, app, client):
        """测试Bug#4: API错误处理中的完整性错误"""
        with app.app_context():
            # 首先创建一个学生
            student_data = {
                'student_id': 'TEST2024003',
                'name': '测试学生API',
                'id_card': '110101200001011113',
                'gender': '男',
                'age': 22,
                'major': '数据科学',
                'grade': '2024'
            }
            
            response = client.post('/api/students', json=student_data)
            assert response.status_code == 201
            
            # 尝试创建重复学号的学生
            duplicate_data = student_data.copy()
            duplicate_data['name'] = '另一个学生'
            duplicate_data['id_card'] = '110101200001011114'
            
            response = client.post('/api/students', json=duplicate_data)
            assert response.status_code == 400
            data = response.get_json()
            assert not data['success']
            assert '学号已存在' in data['message']
            
            # 尝试创建重复身份证的学生
            duplicate_id_card_data = {
                'student_id': 'TEST2024004',
                'name': '重复身份证学生',
                'id_card': '110101200001011113',  # 重复的身份证
                'gender': '女',
                'age': 20,
                'major': '软件工程',
                'grade': '2024'
            }
            
            response = client.post('/api/students', json=duplicate_id_card_data)
            assert response.status_code == 400
            data = response.get_json()
            assert not data['success']
            assert '身份证号已存在' in data['message']
    
    def test_bug_fix_model_cascade_delete(self, app):
        """测试Bug#5: 模型级联删除可能导致的数据完整性问题"""
        with app.app_context():
            # 创建学生、课程、图书
            student = Student.create(
                student_id='TEST2024005',
                name='级联删除测试学生',
                id_card='110101200001011115',
                gender='男',
                age=23,
                major='计算机科学',
                grade='2024'
            )
            
            course = Course.create(
                code='CASCADE101',
                name='级联删除测试课程',
                credits=3,
                teacher='测试老师',
                semester='2024春'
            )
            
            book = Book.create(
                isbn='9787302000003',
                title='级联删除测试图书',
                author='测试作者',
                publisher='测试出版社',
                total_copies=2
            )
            
            # 创建选课记录和借书记录
            enrollment = Enrollment.create(
                student_id=student.id,
                course_id=course.id
            )
            
            borrow_record = BorrowRecord.create(
                student_id=student.id,
                book_id=book.id
            )
            
            # 验证记录存在
            assert Enrollment.query.filter_by(student_id=student.id).count() == 1
            assert BorrowRecord.query.filter_by(student_id=student.id).count() == 1
            
            # 删除学生，验证相关记录也被删除（级联删除）
            student.delete()
            
            # 验证级联删除正常工作
            assert Enrollment.query.filter_by(student_id=student.id).count() == 0
            assert BorrowRecord.query.filter_by(student_id=student.id).count() == 0
            
            # 但课程和图书仍然存在
            assert Course.query.get(course.id) is not None
            assert Book.query.get(book.id) is not None
    
    def test_bug_fix_datetime_timezone_consistency(self, app):
        """测试Bug#6: 时间戳一致性问题"""
        with app.app_context():
            before_create = datetime.utcnow()
            
            student = Student.create(
                student_id='TEST2024006',
                name='时间戳测试学生',
                id_card='110101200001011116',
                gender='女',
                age=19,
                major='数学',
                grade='2024'
            )
            
            after_create = datetime.utcnow()
            
            # 验证创建时间在合理范围内
            assert before_create <= student.created_at <= after_create
            assert student.created_at == student.updated_at
            
            # 更新学生信息
            before_update = datetime.utcnow()
            student.update(age=20)
            after_update = datetime.utcnow()
            
            # 验证更新时间正确
            assert before_update <= student.updated_at <= after_update
            assert student.updated_at > student.created_at
    
    def test_bug_fix_search_empty_results(self, app, client):
        """测试Bug#7: 搜索空结果时的处理"""
        with app.app_context():
            # 测试不存在的搜索
            response = client.get('/students?search=不存在的学生名字')
            assert response.status_code == 200
            
            response = client.get('/courses?search=不存在的课程')
            assert response.status_code == 200
            
            response = client.get('/books?search=不存在的图书')
            assert response.status_code == 200
            
            # API测试
            response = client.get('/api/students?search=不存在的学生')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success']
            assert len(data['data']['students']) == 0
    
    def test_bug_fix_pagination_edge_cases(self, app, client):
        """测试Bug#8: 分页边界情况处理"""
        with app.app_context():
            # 测试超出范围的页码
            response = client.get('/students?page=999')
            assert response.status_code == 200
            
            response = client.get('/api/students?page=999')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success']
            
            # 测试负数页码
            response = client.get('/students?page=-1')
            assert response.status_code == 200
            
            # 测试非数字页码
            response = client.get('/students?page=abc')
            assert response.status_code == 200
