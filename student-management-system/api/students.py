#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生API接口
Student API Resources
"""

from flask import request
from flask_restful import Resource
from models import db, Student
from sqlalchemy.exc import IntegrityError

class StudentListAPI(Resource):
    """学生列表API"""
    
    def get(self):
        """获取学生列表"""
        try:
            # 获取查询参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            search = request.args.get('search', '')
            
            # 构建查询
            if search:
                pagination = Student.search(search, page=page, per_page=per_page)
            else:
                pagination = Student.query.paginate(
                    page=page, per_page=per_page, error_out=False
                )
            
            # 构建响应数据
            students = [student.to_dict() for student in pagination.items]
            
            return {
                'success': True,
                'data': {
                    'students': students,
                    'pagination': {
                        'page': pagination.page,
                        'per_page': pagination.per_page,
                        'total': pagination.total,
                        'pages': pagination.pages,
                        'has_prev': pagination.has_prev,
                        'has_next': pagination.has_next
                    }
                },
                'message': '获取学生列表成功'
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取学生列表失败: {str(e)}'
            }, 500
    
    def post(self):
        """创建新学生"""
        try:
            data = request.get_json()
            
            # 验证必要字段
            required_fields = ['student_id', 'name', 'id_card', 'gender', 'age', 'major', 'grade']
            for field in required_fields:
                if field not in data:
                    return {
                        'success': False,
                        'message': f'缺少必要字段: {field}'
                    }, 400
            
            # 创建学生
            student = Student.create(**data)
            
            return {
                'success': True,
                'data': {'student': student.to_dict()},
                'message': '创建学生成功'
            }, 201
            
        except IntegrityError as e:
            db.session.rollback()
            if 'student_id' in str(e):
                message = '学号已存在'
            elif 'id_card' in str(e):
                message = '身份证号已存在'
            elif 'email' in str(e):
                message = '邮箱已存在'
            else:
                message = '数据完整性错误'
            
            return {
                'success': False,
                'message': message
            }, 400
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'创建学生失败: {str(e)}'
            }, 500

class StudentAPI(Resource):
    """单个学生API"""
    
    def get(self, student_id):
        """获取学生详情"""
        try:
            student = Student.query.get_or_404(student_id)
            
            # 获取详细信息
            student_data = student.to_dict()
            student_data['enrolled_courses'] = [course.to_dict() for course in student.enrolled_courses]
            student_data['borrowed_books'] = [book.to_dict() for book in student.borrowed_books]
            
            return {
                'success': True,
                'data': {'student': student_data},
                'message': '获取学生详情成功'
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取学生详情失败: {str(e)}'
            }, 500
    
    def put(self, student_id):
        """更新学生信息"""
        try:
            student = Student.query.get_or_404(student_id)
            data = request.get_json()
            
            # 更新学生信息
            student.update(**data)
            
            return {
                'success': True,
                'data': {'student': student.to_dict()},
                'message': '更新学生信息成功'
            }, 200
            
        except IntegrityError as e:
            db.session.rollback()
            if 'student_id' in str(e):
                message = '学号已存在'
            elif 'id_card' in str(e):
                message = '身份证号已存在'
            elif 'email' in str(e):
                message = '邮箱已存在'
            else:
                message = '数据完整性错误'
            
            return {
                'success': False,
                'message': message
            }, 400
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'更新学生信息失败: {str(e)}'
            }, 500
    
    def delete(self, student_id):
        """删除学生"""
        try:
            student = Student.query.get_or_404(student_id)
            student_name = student.name
            student.delete()
            
            return {
                'success': True,
                'message': f'删除学生 {student_name} 成功'
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'删除学生失败: {str(e)}'
            }, 500
