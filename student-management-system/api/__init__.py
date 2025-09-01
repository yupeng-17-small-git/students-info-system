#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API模块初始化
API Module Initialization
"""

from flask import Blueprint
from flask_restful import Api

# 创建API蓝图
api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# 导入所有API资源
from .students import StudentListAPI, StudentAPI
from .courses import CourseListAPI, CourseAPI
from .books import BookListAPI, BookAPI
from .enrollments import EnrollmentListAPI, EnrollmentAPI
from .borrows import BorrowListAPI, BorrowAPI
from .dashboard import DashboardAPI

# 注册API路由
# 学生相关API
api.add_resource(StudentListAPI, '/students')
api.add_resource(StudentAPI, '/students/<int:student_id>')

# 课程相关API
api.add_resource(CourseListAPI, '/courses')
api.add_resource(CourseAPI, '/courses/<int:course_id>')

# 图书相关API
api.add_resource(BookListAPI, '/books')
api.add_resource(BookAPI, '/books/<int:book_id>')

# 选课相关API
api.add_resource(EnrollmentListAPI, '/enrollments')
api.add_resource(EnrollmentAPI, '/enrollments/<int:enrollment_id>')

# 借书相关API
api.add_resource(BorrowListAPI, '/borrows')
api.add_resource(BorrowAPI, '/borrows/<int:borrow_id>')

# 仪表板API
api.add_resource(DashboardAPI, '/dashboard')

__all__ = ['api_bp']


# 在 api/__init__.py 中添加错误处理

from functools import wraps
from flask import jsonify
from sqlalchemy.exc import IntegrityError

def handle_api_errors(f):
    """API错误处理装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return {
                'success': False,
                'message': str(e),
                'error_type': 'validation_error'
            }, 400
        except IntegrityError as e:
            from models import db
            db.session.rollback()
            
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            
            if 'UNIQUE constraint failed' in error_msg:
                if 'student_id' in error_msg:
                    message = '学号已存在'
                elif 'id_card' in error_msg:
                    message = '身份证号已存在'
                elif 'isbn' in error_msg:
                    message = 'ISBN已存在'
                elif 'code' in error_msg:
                    message = '课程代码已存在'
                else:
                    message = '数据已存在，请检查唯一性约束'
            else:
                message = '数据库操作失败'
                
            return {
                'success': False,
                'message': message,
                'error_type': 'integrity_error'
            }, 400
        except Exception as e:
            return {
                'success': False,
                'message': f'服务器内部错误: {str(e)}',
                'error_type': 'server_error'
            }, 500
    
    return decorated_function
