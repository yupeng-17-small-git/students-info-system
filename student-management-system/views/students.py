#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生管理视图
Student Management Views
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from . import main_bp
from models import db, Student

@main_bp.route('/students')
def student_list():
    """学生列表页面"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    if search:
        pagination = Student.search(search, page=page, per_page=10)
    else:
        pagination = Student.query.paginate(
            page=page, per_page=10, error_out=False
        )
    
    return render_template('students/list.html', 
                         pagination=pagination, 
                         search=search)

@main_bp.route('/students/add')
def student_add():
    """添加学生页面"""
    return render_template('students/add.html')

@main_bp.route('/students/<int:student_id>')
def student_detail(student_id):
    """学生详情页面"""
    student = Student.query.get_or_404(student_id)
    return render_template('students/detail.html', student=student)

@main_bp.route('/students/<int:student_id>/edit')
def student_edit(student_id):
    """编辑学生页面"""
    student = Student.query.get_or_404(student_id)
    return render_template('students/edit.html', student=student)
