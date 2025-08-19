#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API接口单元测试
API Unit Tests
"""

import pytest
import json
from models import db, Student, Course, Book

class TestStudentAPI:
    """学生API测试"""
    
    def test_get_student_list(self, client, app, sample_student):
        """测试获取学生列表"""
        with app.app_context():
            Student.create(**sample_student)
            
        response = client.get('/api/students')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']['students']) == 1
        assert data['data']['students'][0]['student_id'] == 'TEST001'
    
    def test_create_student(self, client, sample_student):
        """测试创建学生"""
        response = client.post('/api/students', 
                             data=json.dumps(sample_student),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['student']['student_id'] == 'TEST001'
    
    def test_get_student_detail(self, client, app, sample_student):
        """测试获取学生详情"""
        with app.app_context():
            student = Student.create(**sample_student)
            student_id = student.id
        
        response = client.get(f'/api/students/{student_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['student']['name'] == '测试学生'
    
    def test_update_student(self, client, app, sample_student):
        """测试更新学生信息"""
        with app.app_context():
            student = Student.create(**sample_student)
            student_id = student.id
        
        update_data = {'name': '更新后的姓名'}
        response = client.put(f'/api/students/{student_id}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['student']['name'] == '更新后的姓名'
    
    def test_delete_student(self, client, app, sample_student):
        """测试删除学生"""
        with app.app_context():
            student = Student.create(**sample_student)
            student_id = student.id
        
        response = client.delete(f'/api/students/{student_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True

class TestCourseAPI:
    """课程API测试"""
    
    def test_get_course_list(self, client, app, sample_course):
        """测试获取课程列表"""
        with app.app_context():
            Course.create(**sample_course)
        
        response = client.get('/api/courses')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']['courses']) == 1
    
    def test_create_course(self, client, sample_course):
        """测试创建课程"""
        response = client.post('/api/courses',
                             data=json.dumps(sample_course),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True

class TestBookAPI:
    """图书API测试"""
    
    def test_get_book_list(self, client, app, sample_book):
        """测试获取图书列表"""
        with app.app_context():
            Book.create(**sample_book)
        
        response = client.get('/api/books')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']['books']) == 1
    
    def test_create_book(self, client, sample_book):
        """测试创建图书"""
        response = client.post('/api/books',
                             data=json.dumps(sample_book),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True

class TestEnrollmentAPI:
    """选课API测试"""
    
    def test_student_enroll_course(self, client, app, sample_student, sample_course):
        """测试学生选课"""
        with app.app_context():
            student = Student.create(**sample_student)
            course = Course.create(**sample_course)
            
            enrollment_data = {
                'student_id': student.id,
                'course_id': course.id
            }
        
        response = client.post('/api/enrollments',
                             data=json.dumps(enrollment_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True

class TestBorrowAPI:
    """借书API测试"""
    
    def test_student_borrow_book(self, client, app, sample_student, sample_book):
        """测试学生借书"""
        with app.app_context():
            student = Student.create(**sample_student)
            book = Book.create(**sample_book)
            
            borrow_data = {
                'student_id': student.id,
                'book_id': book.id
            }
        
        response = client.post('/api/borrows',
                             data=json.dumps(borrow_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True

class TestDashboardAPI:
    """仪表板API测试"""
    
    def test_get_dashboard_data(self, client, app, sample_student, sample_course, sample_book):
        """测试获取仪表板数据"""
        with app.app_context():
            Student.create(**sample_student)
            Course.create(**sample_course)
            Book.create(**sample_book)
        
        response = client.get('/api/dashboard')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'overview' in data['data']
