#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选课API接口
Enrollment API Resources
"""

from flask import request
from flask_restful import Resource
from models import db, Student, Course, Enrollment
from sqlalchemy.exc import IntegrityError

class EnrollmentListAPI(Resource):
    """选课列表API"""
    
    def get(self):
        """获取选课列表"""
        try:
            # 获取查询参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            student_id = request.args.get('student_id', type=int)
            course_id = request.args.get('course_id', type=int)
            status = request.args.get('status', '')
            
            # 构建查询
            query = Enrollment.query
            
            if student_id:
                query = query.filter(Enrollment.student_id == student_id)
            
            if course_id:
                query = query.filter(Enrollment.course_id == course_id)
            
            if status:
                query = query.filter(Enrollment.status == status)
            
            pagination = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # 构建响应数据
            enrollments = [enrollment.to_dict() for enrollment in pagination.items]
            
            return {
                'success': True,
                'data': {
                    'enrollments': enrollments,
                    'pagination': {
                        'page': pagination.page,
                        'per_page': pagination.per_page,
                        'total': pagination.total,
                        'pages': pagination.pages,
                        'has_prev': pagination.has_prev,
                        'has_next': pagination.has_next
                    }
                },
                'message': '获取选课列表成功'
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取选课列表失败: {str(e)}'
            }, 500
    
    def post(self):
        """学生选课"""
        try:
            data = request.get_json()
            
            # 验证必要字段
            if 'student_id' not in data or 'course_id' not in data:
                return {
                    'success': False,
                    'message': '缺少学生ID或课程ID'
                }, 400
            
            student_id = data['student_id']
            course_id = data['course_id']
            
            # 验证学生和课程是否存在
            student = Student.query.get_or_404(student_id)
            course = Course.query.get_or_404(course_id)
            
            # 检查是否已经选过这门课
            existing_enrollment = Enrollment.get_by_student_and_course(student_id, course_id)
            if existing_enrollment and existing_enrollment.status != 'dropped':
                return {
                    'success': False,
                    'message': '学生已经选择了这门课程'
                }, 400
            
            # 检查课程是否可以选课
            if not course.can_enroll():
                return {
                    'success': False,
                    'message': '课程不可选择（已满员或已关闭）'
                }, 400
            
            # 创建或重新激活选课记录
            if existing_enrollment:
                existing_enrollment.status = 'enrolled'
                existing_enrollment.update()
                enrollment = existing_enrollment
            else:
                enrollment = Enrollment.create(student_id=student_id, course_id=course_id)
            
            return {
                'success': True,
                'data': {'enrollment': enrollment.to_dict()},
                'message': f'学生 {student.name} 成功选择课程 {course.name}'
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'选课失败: {str(e)}'
            }, 500

class EnrollmentAPI(Resource):
    """单个选课记录API"""
    
    def get(self, enrollment_id):
        """获取选课记录详情"""
        try:
            enrollment = Enrollment.query.get_or_404(enrollment_id)
            
            return {
                'success': True,
                'data': {'enrollment': enrollment.to_dict()},
                'message': '获取选课记录成功'
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取选课记录失败: {str(e)}'
            }, 500
    
    def put(self, enrollment_id):
        """更新选课记录（如成绩等）"""
        try:
            enrollment = Enrollment.query.get_or_404(enrollment_id)
            data = request.get_json()
            
            # 特殊处理：如果是完成课程
            if 'grade' in data and data.get('status') == 'completed':
                enrollment.complete_course(grade=data['grade'])
            else:
                enrollment.update(**data)
            
            return {
                'success': True,
                'data': {'enrollment': enrollment.to_dict()},
                'message': '更新选课记录成功'
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'更新选课记录失败: {str(e)}'
            }, 500
    
    def delete(self, enrollment_id):
        """退课"""
        try:
            enrollment = Enrollment.query.get_or_404(enrollment_id)
            student_name = enrollment.student.name
            course_name = enrollment.course.name
            
            # 退课（软删除）
            enrollment.drop_course()
            
            return {
                'success': True,
                'message': f'学生 {student_name} 成功退选课程 {course_name}'
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'退课失败: {str(e)}'
            }, 500
