#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型单元测试
Model Unit Tests
"""

import pytest
from datetime import datetime, timedelta
from models import db, Student, Course, Book, Enrollment, BorrowRecord
from sqlalchemy.exc import IntegrityError

class TestStudentModel:
    """学生模型测试"""
    
    def test_create_student(self, app, sample_student):
        """测试创建学生"""
        with app.app_context():
            student = Student.create(**sample_student)
            assert student.id is not None
            assert student.student_id == 'TEST001'
            assert student.name == '测试学生'
            assert student.status == 'active'
    
    def test_student_unique_constraints(self, app, sample_student):
        """测试学生唯一性约束"""
        with app.app_context():
            Student.create(**sample_student)
            
            # 测试学号唯一性
            with pytest.raises(IntegrityError):
                Student.create(**sample_student)
                db.session.commit()
    
    def test_student_to_dict(self, app, sample_student):
        """测试学生数据转换"""
        with app.app_context():
            student = Student.create(**sample_student)
            data = student.to_dict()
            
            assert data['student_id'] == 'TEST001'
            assert data['name'] == '测试学生'
            assert 'created_at' in data
    
    def test_student_search(self, app, sample_student):
        """测试学生搜索"""
        with app.app_context():
            Student.create(**sample_student)
            
            # 按姓名搜索
            result = Student.search('测试')
            assert result.total == 1
            
            # 按学号搜索
            result = Student.search('TEST001')
            assert result.total == 1

class TestCourseModel:
    """课程模型测试"""
    
    def test_create_course(self, app, sample_course):
        """测试创建课程"""
        with app.app_context():
            course = Course.create(**sample_course)
            assert course.id is not None
            assert course.code == 'TEST101'
            assert course.name == '测试课程'
            assert course.status == 'active'
    
    def test_course_can_enroll(self, app, sample_course):
        """测试课程是否可选"""
        with app.app_context():
            course = Course.create(**sample_course)
            assert course.can_enroll() is True
            
            # 关闭选课
            course.status = 'closed'
            assert course.can_enroll() is False

class TestBookModel:
    """图书模型测试"""
    
    def test_create_book(self, app, sample_book):
        """测试创建图书"""
        with app.app_context():
            book = Book.create(**sample_book)
            assert book.id is not None
            assert book.isbn == '9787302000000'
            assert book.total_copies == 3
            assert book.available_copies == 3
    
    def test_book_can_borrow(self, app, sample_book):
        """测试图书是否可借"""
        with app.app_context():
            book = Book.create(**sample_book)
            assert book.can_borrow() is True
            
            # 设置为不可用
            book.status = 'unavailable'
            assert book.can_borrow() is False

class TestEnrollmentModel:
    """选课模型测试"""
    
    def test_create_enrollment(self, app, sample_student, sample_course):
        """测试创建选课记录"""
        with app.app_context():
            student = Student.create(**sample_student)
            course = Course.create(**sample_course)
            
            enrollment = Enrollment.create(
                student_id=student.id,
                course_id=course.id
            )
            
            assert enrollment.id is not None
            assert enrollment.status == 'enrolled'
            assert enrollment.student.name == '测试学生'
            assert enrollment.course.name == '测试课程'
    
    def test_enrollment_unique_constraint(self, app, sample_student, sample_course):
        """测试选课唯一性约束"""
        with app.app_context():
            student = Student.create(**sample_student)
            course = Course.create(**sample_course)
            
            Enrollment.create(student_id=student.id, course_id=course.id)
            
            # 不能重复选课
            with pytest.raises(IntegrityError):
                Enrollment.create(student_id=student.id, course_id=course.id)
    
    def test_complete_course(self, app, sample_student, sample_course):
        """测试完成课程"""
        with app.app_context():
            student = Student.create(**sample_student)
            course = Course.create(**sample_course)
            enrollment = Enrollment.create(
                student_id=student.id,
                course_id=course.id
            )
            
            # 完成课程并给成绩
            enrollment.complete_course(grade=85)
            
            assert enrollment.status == 'completed'
            assert enrollment.grade == 85
            assert enrollment.grade_letter == 'B'
            assert enrollment.gpa_points == 3.0

class TestBorrowRecordModel:
    """借书记录模型测试"""
    
    def test_create_borrow_record(self, app, sample_student, sample_book):
        """测试创建借书记录"""
        with app.app_context():
            student = Student.create(**sample_student)
            book = Book.create(**sample_book)
            
            borrow_record = BorrowRecord.create(
                student_id=student.id,
                book_id=book.id
            )
            
            assert borrow_record.id is not None
            assert borrow_record.status == 'borrowed'
            assert borrow_record.due_date is not None
            assert not borrow_record.is_overdue
    
    def test_overdue_detection(self, app, sample_student, sample_book):
        """测试逾期检测"""
        with app.app_context():
            student = Student.create(**sample_student)
            book = Book.create(**sample_book)
            
            # 创建已过期的借书记录
            borrow_record = BorrowRecord.create(
                student_id=student.id,
                book_id=book.id
            )
            borrow_record.due_date = datetime.utcnow() - timedelta(days=5)
            db.session.commit()
            
            assert borrow_record.is_overdue is True
            assert borrow_record.days_overdue == 5
    
    def test_return_book(self, app, sample_student, sample_book):
        """测试归还图书"""
        with app.app_context():
            student = Student.create(**sample_student)
            book = Book.create(**sample_book)
            
            borrow_record = BorrowRecord.create(
                student_id=student.id,
                book_id=book.id
            )
            
            # 归还图书
            borrow_record.return_book()
            
            assert borrow_record.status == 'returned'
            assert borrow_record.return_date is not None
    
    def test_extend_due_date(self, app, sample_student, sample_book):
        """测试延长归还日期"""
        with app.app_context():
            student = Student.create(**sample_student)
            book = Book.create(**sample_book)
            
            borrow_record = BorrowRecord.create(
                student_id=student.id,
                book_id=book.id
            )
            original_due_date = borrow_record.due_date
            
            # 延长7天
            borrow_record.extend_due_date(days=7)
            
            expected_date = original_due_date + timedelta(days=7)
            assert borrow_record.due_date.date() == expected_date.date()
