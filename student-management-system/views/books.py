#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图书管理视图
Book Management Views
"""

from flask import render_template, request
from . import main_bp
from models import db, Book

@main_bp.route('/books')
def book_list():
    """图书列表页面"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Book.query
    if search:
        query = query.filter(
            db.or_(
                Book.isbn.contains(search),
                Book.title.contains(search),
                Book.author.contains(search)
            )
        )
    
    pagination = query.paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('books/list.html', 
                         pagination=pagination, 
                         search=search)

@main_bp.route('/books/add')
def book_add():
    """添加图书页面"""
    return render_template('books/add.html')

@main_bp.route('/books/<int:book_id>')
def book_detail(book_id):
    """图书详情页面"""
    book = Book.query.get_or_404(book_id)
    return render_template('books/detail.html', book=book)

@main_bp.route('/books/<int:book_id>/edit')
def book_edit(book_id):
    """编辑图书页面"""
    book = Book.query.get_or_404(book_id)
    return render_template('books/edit.html', book=book)
