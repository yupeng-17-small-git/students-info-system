#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选课管理视图
Enrollment Management Views
"""

from flask import render_template, request
from . import main_bp
from models import db, Enrollment, Student, Course

@main_bp.route('/enrollments')
def enrollment_list():
    """选课列表页面"""
    page = request.args.get('page', 1, type=int)
    student_id = request.args.get('student_id', type=int)
    course_id = request.args.get('course_id', type=int)
    status = request.args.get('status', '')
    
    query = Enrollment.query
    
    if student_id:
        query = query.filter(Enrollment.student_id == student_id)
    if course_id:
        query = query.filter(Enrollment.course_id == course_id)
    if status:
        query = query.filter(Enrollment.status == status)
    
    pagination = query.paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 获取学生和课程列表用于筛选
    students = Student.query.all()
    courses = Course.query.all()
    
    return render_template('enrollments/list.html', 
                         pagination=pagination,
                         students=students,
                         courses=courses,
                         current_student_id=student_id,
                         current_course_id=course_id,
                         current_status=status)

@main_bp.route('/enrollments/add')
def enrollment_add():
    """选课页面"""
    students = Student.query.filter(Student.status == 'active').all()
    courses = Course.query.filter(Course.status == 'active').all()
    return render_template('enrollments/add.html', 
                         students=students, 
                         courses=courses)

@main_bp.route('/enrollments/<int:enrollment_id>')
def enrollment_detail(enrollment_id):
    """选课详情页面"""
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    return render_template('enrollments/detail.html', enrollment=enrollment)
