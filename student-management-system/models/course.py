#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
课程模型
Course Model
"""

from datetime import datetime
from . import db

class Course(db.Model):
    """课程模型类"""
    __tablename__ = 'courses'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 基本信息
    code = db.Column(db.String(20), unique=True, nullable=False, comment='课程代码')
    name = db.Column(db.String(100), nullable=False, comment='课程名称')
    credits = db.Column(db.Integer, nullable=False, comment='学分')
    hours = db.Column(db.Integer, default=0, comment='学时')
    
    # 教学信息
    teacher = db.Column(db.String(50), nullable=False, comment='授课教师')
    semester = db.Column(db.String(20), nullable=False, comment='开课学期')
    classroom = db.Column(db.String(50), comment='上课教室')
    schedule = db.Column(db.String(100), comment='上课时间')
    
    # 课程详情
    description = db.Column(db.Text, comment='课程描述')
    prerequisites = db.Column(db.String(200), comment='先修课程')
    max_students = db.Column(db.Integer, default=50, comment='最大选课人数')
    
    # 状态信息
    status = db.Column(db.String(20), default='active', comment='状态：active-开放选课，closed-关闭选课，finished-已结束')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    enrollments = db.relationship('Enrollment', back_populates='course', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Course, self).__init__(**kwargs)
    
    def __repr__(self):
        return f'<Course {self.code}: {self.name}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'credits': self.credits,
            'hours': self.hours,
            'teacher': self.teacher,
            'semester': self.semester,
            'classroom': self.classroom,
            'schedule': self.schedule,
            'description': self.description,
            'prerequisites': self.prerequisites,
            'max_students': self.max_students,
            'current_students': self.current_students_count,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create(cls, **kwargs):
        """创建课程记录"""
        course = cls(**kwargs)
        db.session.add(course)
        db.session.commit()
        return course
    
    def update(self, **kwargs):
        """更新课程信息"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
    
    def delete(self):
        """删除课程记录"""
        db.session.delete(self)
        db.session.commit()
    
    @property
    def current_students_count(self):
        """当前选课学生数量"""
        from .enrollment import Enrollment
        return Enrollment.query.filter(
            Enrollment.course_id == self.id,
            Enrollment.status == 'enrolled'
        ).count()
    
    @property
    def enrolled_students(self):
        """获取已选课学生"""
        from .student import Student
        return db.session.query(Student).join(Enrollment).filter(
            Enrollment.course_id == self.id,
            Enrollment.status == 'enrolled'
        ).all()
    
    def can_enroll(self):
        """检查是否可以选课"""
        return (
            self.status == 'active' and 
            self.current_students_count < self.max_students
        )
    
    @staticmethod
    def search(keyword, page=1, per_page=10):
        """搜索课程"""
        query = Course.query.filter(
            db.or_(
                Course.code.contains(keyword),
                Course.name.contains(keyword),
                Course.teacher.contains(keyword),
                Course.semester.contains(keyword)
            )
        )
        return query.paginate(
            page=page, per_page=per_page, error_out=False
        )
