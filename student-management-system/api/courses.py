#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
课程API接口
Course API Resources
"""

from flask import request
from flask_restful import Resource
from models import db, Course
from sqlalchemy.exc import IntegrityError

class CourseListAPI(Resource):
    """课程列表API"""
    
    def get(self):
        """获取课程列表"""
        try:
            # 获取查询参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            search = request.args.get('search', '')
            semester = request.args.get('semester', '')
            status = request.args.get('status', '')
            
            # 构建查询
            query = Course.query
            
            if search:
                query = query.filter(
                    db.or_(
                        Course.code.contains(search),
                        Course.name.contains(search),
                        Course.teacher.contains(search)
                    )
                )
            
            if semester:
                query = query.filter(Course.semester == semester)
            
            if status:
                query = query.filter(Course.status == status)
            
            pagination = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # 构建响应数据
            courses = [course.to_dict() for course in pagination.items]
            
            return {
                'success': True,
                'data': {
                    'courses': courses,
                    'pagination': {
                        'page': pagination.page,
                        'per_page': pagination.per_page,
                        'total': pagination.total,
                        'pages': pagination.pages,
                        'has_prev': pagination.has_prev,
                        'has_next': pagination.has_next
                    }
                },
                'message': '获取课程列表成功'
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取课程列表失败: {str(e)}'
            }, 500
    
    def post(self):
        """创建新课程"""
        try:
            data = request.get_json()
            
            # 验证必要字段
            required_fields = ['code', 'name', 'credits', 'teacher', 'semester']
            for field in required_fields:
                if field not in data:
                    return {
                        'success': False,
                        'message': f'缺少必要字段: {field}'
                    }, 400
            
            # 创建课程
            course = Course.create(**data)
            
            return {
                'success': True,
                'data': {'course': course.to_dict()},
                'message': '创建课程成功'
            }, 201
            
        except IntegrityError as e:
            db.session.rollback()
            return {
                'success': False,
                'message': '课程代码已存在'
            }, 400
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'创建课程失败: {str(e)}'
            }, 500

class CourseAPI(Resource):
    """单个课程API"""
    
    def get(self, course_id):
        """获取课程详情"""
        try:
            course = Course.query.get_or_404(course_id)
            
            # 获取详细信息
            course_data = course.to_dict()
            course_data['enrolled_students'] = [student.to_dict() for student in course.enrolled_students]
            
            return {
                'success': True,
                'data': {'course': course_data},
                'message': '获取课程详情成功'
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取课程详情失败: {str(e)}'
            }, 500
    
    def put(self, course_id):
        """更新课程信息"""
        try:
            course = Course.query.get_or_404(course_id)
            data = request.get_json()
            
            # 更新课程信息
            course.update(**data)
            
            return {
                'success': True,
                'data': {'course': course.to_dict()},
                'message': '更新课程信息成功'
            }, 200
            
        except IntegrityError as e:
            db.session.rollback()
            return {
                'success': False,
                'message': '课程代码已存在'
            }, 400
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'更新课程信息失败: {str(e)}'
            }, 500
    
    def delete(self, course_id):
        """删除课程"""
        try:
            course = Course.query.get_or_404(course_id)
            course_name = course.name
            
            # 检查是否有学生选了这门课
            if course.current_students_count > 0:
                return {
                    'success': False,
                    'message': '该课程还有学生选课，无法删除'
                }, 400
            
            course.delete()
            
            return {
                'success': True,
                'message': f'删除课程 {course_name} 成功'
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'删除课程失败: {str(e)}'
            }, 500
