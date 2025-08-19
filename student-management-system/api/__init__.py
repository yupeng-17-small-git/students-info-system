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
