#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
课程管理视图
Course Management Views
"""

from flask import render_template, request
from . import main_bp
from models import db, Course

@main_bp.route('/courses')
def course_list():
    """课程列表页面"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Course.query
    if search:
        query = query.filter(
            db.or_(
                Course.code.contains(search),
                Course.name.contains(search),
                Course.teacher.contains(search)
            )
        )
    
    pagination = query.paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('courses/list.html', 
                         pagination=pagination, 
                         search=search)

@main_bp.route('/courses/add')
def course_add():
    """添加课程页面"""
    return render_template('courses/add.html')

@main_bp.route('/courses/<int:course_id>')
def course_detail(course_id):
    """课程详情页面"""
    course = Course.query.get_or_404(course_id)
    return render_template('courses/detail.html', course=course)

@main_bp.route('/courses/<int:course_id>/edit')
def course_edit(course_id):
    """编辑课程页面"""
    course = Course.query.get_or_404(course_id)
    return render_template('courses/edit.html', course=course)
