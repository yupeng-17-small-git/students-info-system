#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图书API接口
Book API Resources
"""

from flask import request
from flask_restful import Resource
from models import db, Book
from sqlalchemy.exc import IntegrityError

class BookListAPI(Resource):
    """图书列表API"""
    
    def get(self):
        """获取图书列表"""
        try:
            # 获取查询参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            search = request.args.get('search', '')
            category = request.args.get('category', '')
            status = request.args.get('status', '')
            available_only = request.args.get('available_only', False, type=bool)
            
            # 构建查询
            query = Book.query
            
            if search:
                query = query.filter(
                    db.or_(
                        Book.isbn.contains(search),
                        Book.title.contains(search),
                        Book.author.contains(search),
                        Book.publisher.contains(search)
                    )
                )
            
            if category:
                query = query.filter(Book.category == category)
            
            if status:
                query = query.filter(Book.status == status)
            
            if available_only:
                query = query.filter(Book.status == 'available')
            
            pagination = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # 构建响应数据
            books = [book.to_dict() for book in pagination.items]
            
            return {
                'success': True,
                'data': {
                    'books': books,
                    'pagination': {
                        'page': pagination.page,
                        'per_page': pagination.per_page,
                        'total': pagination.total,
                        'pages': pagination.pages,
                        'has_prev': pagination.has_prev,
                        'has_next': pagination.has_next
                    }
                },
                'message': '获取图书列表成功'
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取图书列表失败: {str(e)}'
            }, 500
    
    def post(self):
        """创建新图书"""
        try:
            data = request.get_json()
            
            # 验证必要字段
            required_fields = ['isbn', 'title', 'author', 'publisher']
            for field in required_fields:
                if field not in data:
                    return {
                        'success': False,
                        'message': f'缺少必要字段: {field}'
                    }, 400
            
            # 创建图书
            book = Book.create(**data)
            
            return {
                'success': True,
                'data': {'book': book.to_dict()},
                'message': '创建图书成功'
            }, 201
            
        except IntegrityError as e:
            db.session.rollback()
            return {
                'success': False,
                'message': 'ISBN号已存在'
            }, 400
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'创建图书失败: {str(e)}'
            }, 500

class BookAPI(Resource):
    """单个图书API"""
    
    def get(self, book_id):
        """获取图书详情"""
        try:
            book = Book.query.get_or_404(book_id)
            
            # 获取详细信息
            book_data = book.to_dict()
            book_data['current_borrowers'] = [borrower.to_dict() for borrower in book.current_borrowers]
            
            return {
                'success': True,
                'data': {'book': book_data},
                'message': '获取图书详情成功'
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取图书详情失败: {str(e)}'
            }, 500
    
    def put(self, book_id):
        """更新图书信息"""
        try:
            book = Book.query.get_or_404(book_id)
            data = request.get_json()
            
            # 更新图书信息
            book.update(**data)
            
            return {
                'success': True,
                'data': {'book': book.to_dict()},
                'message': '更新图书信息成功'
            }, 200
            
        except IntegrityError as e:
            db.session.rollback()
            return {
                'success': False,
                'message': 'ISBN号已存在'
            }, 400
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'更新图书信息失败: {str(e)}'
            }, 500
    
    def delete(self, book_id):
        """删除图书"""
        try:
            book = Book.query.get_or_404(book_id)
            book_title = book.title
            
            # 检查是否有未归还的借阅记录
            if book.borrowed_copies > 0:
                return {
                    'success': False,
                    'message': '该图书还有未归还的借阅记录，无法删除'
                }, 400
            
            book.delete()
            
            return {
                'success': True,
                'message': f'删除图书 {book_title} 成功'
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'删除图书失败: {str(e)}'
            }, 500
