#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视图层测试
View Layer Tests

测试所有视图的功能和错误处理
"""

import pytest
from flask import url_for
from datetime import datetime, timedelta
from models import db, Student, Course, Book, Enrollment, BorrowRecord

class TestStudentViews:
    """学生视图测试"""
    
    def test_student_list_view(self, app, client):
        """测试学生列表页面"""
        with app.app_context():
            response = client.get('/students')
            assert response.status_code == 200
    
    def test_student_list_with_search(self, app, client):
        """测试学生列表搜索功能"""
        with app.app_context():
            student = Student.create(
                student_id='SEARCH001',
                name='搜索测试学生',
                id_card='110101200001011201',
                gender='男',
                age=20,
                major='计算机科学',
                grade='2024'
            )
            
            response = client.get('/students?search=搜索测试')
            assert response.status_code == 200
            
            response = client.get('/students?search=SEARCH001')
            assert response.status_code == 200
    
    def test_student_detail_view(self, app, client):
        """测试学生详情页面"""
        with app.app_context():
            student = Student.create(
                student_id='DETAIL001',
                name='详情测试学生',
                id_card='110101200001011301',
                gender='女',
                age=21,
                major='软件工程',
                grade='2024'
            )
            
            response = client.get(f'/students/{student.id}')
            assert response.status_code == 200
    
    def test_student_not_found(self, app, client):
        """测试学生不存在的情况"""
        with app.app_context():
            response = client.get('/students/99999')
            assert response.status_code == 404

class TestCourseViews:
    """课程视图测试"""
    
    def test_course_list_view(self, app, client):
        """测试课程列表页面"""
        with app.app_context():
            response = client.get('/courses')
            assert response.status_code == 200
    
    def test_course_list_with_search(self, app, client):
        """测试课程列表搜索功能"""
        with app.app_context():
            course = Course.create(
                code='SEARCH101',
                name='搜索测试课程Python编程',
                credits=3,
                teacher='张教授',
                semester='2024春'
            )
            
            response = client.get('/courses?search=Python')
            assert response.status_code == 200
    
    def test_course_detail_view(self, app, client):
        """测试课程详情页面"""
        with app.app_context():
            course = Course.create(
                code='DETAIL101',
                name='详情测试课程',
                credits=4,
                teacher='李教授',
                semester='2024春'
            )
            
            response = client.get(f'/courses/{course.id}')
            assert response.status_code == 200

class TestBookViews:
    """图书视图测试"""
    
    def test_book_list_view(self, app, client):
        """测试图书列表页面"""
        with app.app_context():
            response = client.get('/books')
            assert response.status_code == 200
    
    def test_book_list_with_search(self, app, client):
        """测试图书列表搜索功能"""
        with app.app_context():
            book = Book.create(
                isbn='9787302111111',
                title='Python高级编程搜索测试',
                author='测试作者',
                publisher='人民邮电出版社',
                total_copies=5
            )
            
            response = client.get('/books?search=Python高级')
            assert response.status_code == 200

class TestDashboardViews:
    """仪表板视图测试"""
    
    def test_dashboard_view(self, app, client):
        """测试仪表板页面"""
        with app.app_context():
            response = client.get('/dashboard')
            assert response.status_code == 200
    
    def test_index_redirect(self, app, client):
        """测试首页重定向"""
        with app.app_context():
            response = client.get('/', follow_redirects=False)
            assert response.status_code == 302
            assert '/dashboard' in response.location
    
    def test_404_error_page(self, app, client):
        """测试404错误页面"""
        with app.app_context():
            response = client.get('/nonexistent-page')
            assert response.status_code == 404
