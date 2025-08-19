#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仪表板API接口
Dashboard API Resources
"""

from flask import request
from flask_restful import Resource
from models import db, Student, Course, Book, Enrollment, BorrowRecord
from datetime import datetime, timedelta
from sqlalchemy import func, and_

class DashboardAPI(Resource):
    """仪表板API"""
    
    def get(self):
        """获取仪表板统计数据"""
        try:
            # 基础统计
            total_students = Student.query.count()
            total_courses = Course.query.count()
            total_books = Book.query.count()
            
            # 学生统计
            active_students = Student.query.filter(Student.status == 'active').count()
            
            # 课程统计
            active_courses = Course.query.filter(Course.status == 'active').count()
            total_enrollments = Enrollment.query.filter(Enrollment.status == 'enrolled').count()
            
            # 图书统计
            available_books = Book.query.filter(Book.status == 'available').count()
            total_book_copies = db.session.query(func.sum(Book.total_copies)).scalar() or 0
            borrowed_books = BorrowRecord.query.filter(BorrowRecord.status == 'borrowed').count()
            available_copies = total_book_copies - borrowed_books
            
            # 借阅统计
            overdue_books = BorrowRecord.query.filter(
                BorrowRecord.status == 'borrowed',
                BorrowRecord.due_date < datetime.utcnow()
            ).count()
            
            # 最近7天的统计
            week_ago = datetime.utcnow() - timedelta(days=7)
            new_students_this_week = Student.query.filter(Student.created_at >= week_ago).count()
            new_enrollments_this_week = Enrollment.query.filter(Enrollment.created_at >= week_ago).count()
            new_borrows_this_week = BorrowRecord.query.filter(BorrowRecord.borrow_date >= week_ago).count()
            
            # 专业分布统计
            major_stats = db.session.query(
                Student.major, 
                func.count(Student.id).label('count')
            ).group_by(Student.major).all()
            
            # 年级分布统计
            grade_stats = db.session.query(
                Student.grade, 
                func.count(Student.id).label('count')
            ).group_by(Student.grade).all()
            
            # 热门课程（按选课人数）
            popular_courses = db.session.query(
                Course.name,
                Course.code,
                func.count(Enrollment.id).label('enrollment_count')
            ).join(Enrollment).filter(
                Enrollment.status == 'enrolled'
            ).group_by(Course.id).order_by(
                func.count(Enrollment.id).desc()
            ).limit(5).all()
            
            # 热门图书（按借阅次数）
            popular_books = db.session.query(
                Book.title,
                Book.author,
                func.count(BorrowRecord.id).label('borrow_count')
            ).join(BorrowRecord).group_by(Book.id).order_by(
                func.count(BorrowRecord.id).desc()
            ).limit(5).all()
            
            # 最近活动
            recent_enrollments = db.session.query(Enrollment).join(
                Student
            ).join(Course).filter(
                Enrollment.status == 'enrolled'
            ).order_by(Enrollment.created_at.desc()).limit(10).all()
            
            recent_borrows = db.session.query(BorrowRecord).join(
                Student
            ).join(Book).filter(
                BorrowRecord.status == 'borrowed'
            ).order_by(BorrowRecord.borrow_date.desc()).limit(10).all()
            
            # 构建响应数据
            dashboard_data = {
                # 基础统计
                'overview': {
                    'total_students': total_students,
                    'active_students': active_students,
                    'total_courses': total_courses,
                    'active_courses': active_courses,
                    'total_books': total_books,
                    'available_books': available_books,
                    'total_book_copies': total_book_copies,
                    'available_copies': available_copies,
                    'borrowed_books': borrowed_books,
                    'overdue_books': overdue_books,
                    'total_enrollments': total_enrollments
                },
                
                # 本周统计
                'this_week': {
                    'new_students': new_students_this_week,
                    'new_enrollments': new_enrollments_this_week,
                    'new_borrows': new_borrows_this_week
                },
                
                # 分布统计
                'distributions': {
                    'majors': [{
                        'major': major,
                        'count': count
                    } for major, count in major_stats],
                    'grades': [{
                        'grade': grade,
                        'count': count
                    } for grade, count in grade_stats]
                },
                
                # 热门数据
                'popular': {
                    'courses': [{
                        'name': name,
                        'code': code,
                        'enrollment_count': count
                    } for name, code, count in popular_courses],
                    'books': [{
                        'title': title,
                        'author': author,
                        'borrow_count': count
                    } for title, author, count in popular_books]
                },
                
                # 最近活动
                'recent_activities': {
                    'enrollments': [{
                        'student_name': enrollment.student.name,
                        'course_name': enrollment.course.name,
                        'date': enrollment.created_at.isoformat()
                    } for enrollment in recent_enrollments],
                    'borrows': [{
                        'student_name': borrow.student.name,
                        'book_title': borrow.book.title,
                        'date': borrow.borrow_date.isoformat()
                    } for borrow in recent_borrows]
                }
            }
            
            return {
                'success': True,
                'data': dashboard_data,
                'message': '获取仪表板数据成功'
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取仪表板数据失败: {str(e)}'
            }, 500
