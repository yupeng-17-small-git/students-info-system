#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仪表板视图
Dashboard Views
"""

from flask import render_template, request, jsonify
from . import main_bp
from models import db, Student, Course, Book, Enrollment, BorrowRecord
from datetime import datetime, timedelta
from sqlalchemy import func

@main_bp.route('/dashboard')
def dashboard():
    """仪表板主页"""
    return render_template('dashboard.html')

@main_bp.route('/api/dashboard/stats')
def dashboard_stats():
    """获取仪表板统计数据（内部API）"""
    try:
        # 基础统计
        stats = {
            'students': {
                'total': Student.query.count(),
                'active': Student.query.filter(Student.status == 'active').count()
            },
            'courses': {
                'total': Course.query.count(),
                'active': Course.query.filter(Course.status == 'active').count()
            },
            'books': {
                'total': Book.query.count(),
                'available': Book.query.filter(Book.status == 'available').count(),
                'borrowed': BorrowRecord.query.filter(BorrowRecord.status == 'borrowed').count()
            },
            'enrollments': {
                'total': Enrollment.query.filter(Enrollment.status == 'enrolled').count()
            }
        }
        
        # 逾期图书
        overdue_count = BorrowRecord.query.filter(
            BorrowRecord.status == 'borrowed',
            BorrowRecord.due_date < datetime.utcnow()
        ).count()
        stats['books']['overdue'] = overdue_count
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
