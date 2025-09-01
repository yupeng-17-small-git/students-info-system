#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API完整测试
Complete API Tests

测试所有API端点的完整功能和边界情况
"""

import pytest
import json
from datetime import datetime, timedelta
from models import db, Student, Course, Book, Enrollment, BorrowRecord

class TestStudentAPI:
    """学生API完整测试"""
    
    def test_create_student_success(self, app, client, sample_student):
        """测试成功创建学生"""
        with app.app_context():
            response = client.post('/api/students', 
                                 json=sample_student,
                                 content_type='application/json')
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['success']
            assert data['data']['student']['student_id'] == sample_student['student_id']
    
    def test_create_student_missing_fields(self, app, client):
        """测试创建学生缺少必要字段"""
        with app.app_context():
            incomplete_data = {
                'name': '不完整学生',
                'gender': '男'
            }
            
            response = client.post('/api/students', json=incomplete_data)
            assert response.status_code == 400
            data = response.get_json()
            assert not data['success']
            assert '缺少必要字段' in data['message']
    
    def test_get_students_list(self, app, client):
        """测试获取学生列表"""
        with app.app_context():
            for i in range(3):
                Student.create(
                    student_id=f'API{i:03d}',
                    name=f'API测试学生{i}',
                    id_card=f'11010120000201{i:04d}',
                    gender='男' if i % 2 == 0 else '女',
                    age=20 + i,
                    major='计算机科学',
                    grade='2024'
                )
            
            response = client.get('/api/students')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success']
            assert 'students' in data['data']
    
    def test_update_student(self, app, client, sample_student):
        """测试更新学生信息"""
        with app.app_context():
            response = client.post('/api/students', json=sample_student)
            student_id = response.get_json()['data']['student']['id']
            
            update_data = {'age': 25, 'major': '软件工程'}
            response = client.put(f'/api/students/{student_id}', json=update_data)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success']
            assert data['data']['student']['age'] == 25

class TestCourseAPI:
    """课程API测试"""
    
    def test_create_course_success(self, app, client, sample_course):
        """测试成功创建课程"""
        with app.app_context():
            response = client.post('/api/courses', json=sample_course)
            assert response.status_code == 201
            data = response.get_json()
            assert data['success']
    
    def test_get_courses_list(self, app, client):
        """测试获取课程列表"""
        with app.app_context():
            response = client.get('/api/courses')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success']

class TestBookAPI:
    """图书API测试"""
    
    def test_create_book_success(self, app, client, sample_book):
        """测试成功创建图书"""
        with app.app_context():
            response = client.post('/api/books', json=sample_book)
            assert response.status_code == 201
            data = response.get_json()
            assert data['success']
    
    def test_get_books_list(self, app, client):
        """测试获取图书列表"""
        with app.app_context():
            response = client.get('/api/books')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success']

class TestEnrollmentAPI:
    """选课API测试"""
    
    def test_create_enrollment(self, app, client):
        """测试创建选课记录"""
        with app.app_context():
            student = Student.create(
                student_id='ENROLL001',
                name='选课学生',
                id_card='110101200001011801',
                gender='男',
                age=20,
                major='计算机科学',
                grade='2024'
            )
            
            course = Course.create(
                code='ENROLL101',
                name='选课课程',
                credits=3,
                teacher='选课教师',
                semester='2024春'
            )
            
            enrollment_data = {
                'student_id': student.id,
                'course_id': course.id
            }
            
            response = client.post('/api/enrollments', json=enrollment_data)
            assert response.status_code == 201
            data = response.get_json()
            assert data['success']

class TestBorrowAPI:
    """借书API测试"""
    
    def test_create_borrow_record(self, app, client):
        """测试创建借书记录"""
        with app.app_context():
            student = Student.create(
                student_id='BORROW001',
                name='借书学生',
                id_card='110101200001011901',
                gender='女',
                age=21,
                major='软件工程',
                grade='2024'
            )
            
            book = Book.create(
                isbn='9787302888888',
                title='借书测试图书',
                author='借书作者',
                publisher='借书出版社',
                total_copies=3
            )
            
            borrow_data = {
                'student_id': student.id,
                'book_id': book.id
            }
            
            response = client.post('/api/borrows', json=borrow_data)
            assert response.status_code == 201
            data = response.get_json()
            assert data['success']

class TestDashboardAPI:
    """仪表板API测试"""
    
    def test_dashboard_stats(self, app, client):
        """测试仪表板统计"""
        with app.app_context():
            response = client.get('/api/dashboard/stats')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success']
            assert 'students' in data['data']
            assert 'courses' in data['data']
            assert 'books' in data['data']
