#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
借书API接口
Borrow API Resources
"""

from flask import request
from flask_restful import Resource
from models import db, Student, Book, BorrowRecord
from datetime import datetime, timedelta

class BorrowListAPI(Resource):
    """借书列表API"""
    
    def get(self):
        """获取借书列表"""
        try:
            # 获取查询参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            student_id = request.args.get('student_id', type=int)
            book_id = request.args.get('book_id', type=int)
            status = request.args.get('status', '')
            overdue_only = request.args.get('overdue_only', False, type=bool)
            
            # 构建查询
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
                page=page, per_page=per_page, error_out=False
            )
            
            # 构建响应数据
            borrows = [borrow.to_dict() for borrow in pagination.items]
            
            return {
                'success': True,
                'data': {
                    'borrows': borrows,
                    'pagination': {
                        'page': pagination.page,
                        'per_page': pagination.per_page,
                        'total': pagination.total,
                        'pages': pagination.pages,
                        'has_prev': pagination.has_prev,
                        'has_next': pagination.has_next
                    }
                },
                'message': '获取借书列表成功'
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取借书列表失败: {str(e)}'
            }, 500
    
    def post(self):
        """学生借书"""
        try:
            data = request.get_json()
            
            # 验证必要字段
            if 'student_id' not in data or 'book_id' not in data:
                return {
                    'success': False,
                    'message': '缺少学生ID或图书ID'
                }, 400
            
            student_id = data['student_id']
            book_id = data['book_id']
            
            # 验证学生和图书是否存在
            student = Student.query.get_or_404(student_id)
            book = Book.query.get_or_404(book_id)
            
            # 检查学生是否已经借了这本书
            existing_borrow = BorrowRecord.get_by_student_and_book(student_id, book_id)
            if existing_borrow:
                return {
                    'success': False,
                    'message': '学生已经借阅了这本书'
                }, 400
            
            # 检查图书是否可以借阅
            if not book.can_borrow():
                return {
                    'success': False,
                    'message': '图书不可借阅（无库存或不可用）'
                }, 400
            
            # 检查学生借书数量限制（最多借5本）
            current_borrows = len(student.borrowed_books)
            if current_borrows >= 5:
                return {
                    'success': False,
                    'message': '学生借书数量已达上限（5本）'
                }, 400
            
            # 创建借书记录
            borrow_record = BorrowRecord.create(
                student_id=student_id,
                book_id=book_id,
                due_date=datetime.utcnow() + timedelta(days=30)  # 30天后归还
            )
            
            return {
                'success': True,
                'data': {'borrow_record': borrow_record.to_dict()},
                'message': f'学生 {student.name} 成功借阅图书 {book.title}'
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'借书失败: {str(e)}'
            }, 500

class BorrowAPI(Resource):
    """单个借书记录API"""
    
    def get(self, borrow_id):
        """获取借书记录详情"""
        try:
            borrow_record = BorrowRecord.query.get_or_404(borrow_id)
            
            return {
                'success': True,
                'data': {'borrow_record': borrow_record.to_dict()},
                'message': '获取借书记录成功'
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取借书记录失败: {str(e)}'
            }, 500
    
    def put(self, borrow_id):
        """更新借书记录（归还、续借等）"""
        try:
            borrow_record = BorrowRecord.query.get_or_404(borrow_id)
            data = request.get_json()
            action = data.get('action')
            
            if action == 'return':
                # 归还图书
                fine_amount = data.get('fine_amount')
                borrow_record.return_book(fine_amount=fine_amount)
                message = f'图书 {borrow_record.book.title} 归还成功'
                
            elif action == 'extend':
                # 续借（延长7天）
                days = data.get('days', 7)
                borrow_record.extend_due_date(days=days)
                message = f'图书 {borrow_record.book.title} 续借成功，延长 {days} 天'
                
            elif action == 'lost':
                # 标记为丢失
                fine_amount = data.get('fine_amount', 50.0)  # 默认丢失罚金50元
                borrow_record.mark_lost(fine_amount=fine_amount)
                message = f'图书 {borrow_record.book.title} 已标记为丢失'
                
            elif action == 'pay_fine':
                # 支付罚金
                borrow_record.pay_fine()
                message = '罚金支付成功'
                
            else:
                # 普通更新
                borrow_record.update(**data)
                message = '更新借书记录成功'
            
            return {
                'success': True,
                'data': {'borrow_record': borrow_record.to_dict()},
                'message': message
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'更新借书记录失败: {str(e)}'
            }, 500
    
    def delete(self, borrow_id):
        """删除借书记录（仅用于管理员清理无效记录）"""
        try:
            borrow_record = BorrowRecord.query.get_or_404(borrow_id)
            
            # 只允许删除已归还或丢失的记录
            if borrow_record.status not in ['returned', 'lost']:
                return {
                    'success': False,
                    'message': '只能删除已归还或丢失的借书记录'
                }, 400
            
            student_name = borrow_record.student.name
            book_title = borrow_record.book.title
            borrow_record.delete()
            
            return {
                'success': True,
                'message': f'删除借书记录成功（学生: {student_name}, 图书: {book_title}）'
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'删除借书记录失败: {str(e)}'
            }, 500
