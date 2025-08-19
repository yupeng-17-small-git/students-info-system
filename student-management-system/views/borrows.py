#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
借书管理视图
Borrow Management Views
"""

from flask import render_template, request
from . import main_bp
from models import db, BorrowRecord, Student, Book
from datetime import datetime

@main_bp.route('/borrows')
def borrow_list():
    """借书列表页面"""
    page = request.args.get('page', 1, type=int)
    student_id = request.args.get('student_id', type=int)
    book_id = request.args.get('book_id', type=int)
    status = request.args.get('status', '')
    overdue_only = request.args.get('overdue_only', False, type=bool)
    
    query = BorrowRecord.query
    
    if student_id:
        query = query.filter(BorrowRecord.student_id == student_id)
    if book_id:
        query = query.filter(BorrowRecord.book_id == book_id)
    if status:
        query = query.filter(BorrowRecord.status == status)
    if overdue_only:
        query = query.filter(
            BorrowRecord.status == 'borrowed',
            BorrowRecord.due_date < datetime.utcnow()
        )
    
    pagination = query.order_by(BorrowRecord.borrow_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 获取学生和图书列表用于筛选
    students = Student.query.all()
    books = Book.query.all()
    
    return render_template('borrows/list.html', 
                         pagination=pagination,
                         students=students,
                         books=books,
                         current_student_id=student_id,
                         current_book_id=book_id,
                         current_status=status,
                         overdue_only=overdue_only)

@main_bp.route('/borrows/add')
def borrow_add():
    """借书页面"""
    students = Student.query.filter(Student.status == 'active').all()
    books = Book.query.filter(Book.status == 'available').all()
    return render_template('borrows/add.html', 
                         students=students, 
                         books=books)

@main_bp.route('/borrows/<int:borrow_id>')
def borrow_detail(borrow_id):
    """借书详情页面"""
    borrow_record = BorrowRecord.query.get_or_404(borrow_id)
    return render_template('borrows/detail.html', borrow_record=borrow_record)

@main_bp.route('/borrows/overdue')
def borrow_overdue():
    """逾期图书页面"""
    overdue_records = BorrowRecord.query.filter(
        BorrowRecord.status == 'borrowed',
        BorrowRecord.due_date < datetime.utcnow()
    ).order_by(BorrowRecord.due_date.asc()).all()
    
    return render_template('borrows/overdue.html', 
                         overdue_records=overdue_records)
