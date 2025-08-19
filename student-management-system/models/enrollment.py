#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选课记录模型
Enrollment Model
"""

from datetime import datetime
from . import db

class Enrollment(db.Model):
    """选课记录模型类"""
    __tablename__ = 'enrollments'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 外键关联
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, comment='学生ID')
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, comment='课程ID')
    
    # 选课信息
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow, comment='选课日期')
    status = db.Column(db.String(20), default='enrolled', comment='状态：enrolled-已选课，dropped-已退课，completed-已完成')
    
    # 成绩信息
    grade = db.Column(db.Float, comment='成绩')
    grade_letter = db.Column(db.String(5), comment='等级成绩')
    gpa_points = db.Column(db.Float, comment='绩点')
    
    # 备注信息
    notes = db.Column(db.Text, comment='备注')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    student = db.relationship('Student', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')
    
    # 唯一约束：一个学生不能重复选择同一门课程
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='uq_student_course'),)
    
    def __init__(self, **kwargs):
        super(Enrollment, self).__init__(**kwargs)
    
    def __repr__(self):
        return f'<Enrollment Student:{self.student_id} Course:{self.course_id}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'student_name': self.student.name if self.student else None,
            'student_student_id': self.student.student_id if self.student else None,
            'course_name': self.course.name if self.course else None,
            'course_code': self.course.code if self.course else None,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'status': self.status,
            'grade': self.grade,
            'grade_letter': self.grade_letter,
            'gpa_points': self.gpa_points,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create(cls, **kwargs):
        """创建选课记录"""
        enrollment = cls(**kwargs)
        db.session.add(enrollment)
        db.session.commit()
        return enrollment
    
    def update(self, **kwargs):
        """更新选课记录"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
    
    def delete(self):
        """删除选课记录"""
        db.session.delete(self)
        db.session.commit()
    
    def drop_course(self):
        """退课"""
        self.status = 'dropped'
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
    
    def complete_course(self, grade=None, grade_letter=None):
        """完成课程"""
        self.status = 'completed'
        if grade is not None:
            self.grade = grade
            # 根据成绩计算等级和绩点
            if grade >= 90:
                self.grade_letter = 'A'
                self.gpa_points = 4.0
            elif grade >= 80:
                self.grade_letter = 'B'
                self.gpa_points = 3.0
            elif grade >= 70:
                self.grade_letter = 'C'
                self.gpa_points = 2.0
            elif grade >= 60:
                self.grade_letter = 'D'
                self.gpa_points = 1.0
            else:
                self.grade_letter = 'F'
                self.gpa_points = 0.0
        if grade_letter is not None:
            self.grade_letter = grade_letter
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
    
    @staticmethod
    def get_by_student_and_course(student_id, course_id):
        """根据学生和课程获取选课记录"""
        return Enrollment.query.filter(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id
        ).first()
    
    @staticmethod
    def get_student_enrollments(student_id, status=None):
        """获取学生的选课记录"""
        query = Enrollment.query.filter(Enrollment.student_id == student_id)
        if status:
            query = query.filter(Enrollment.status == status)
        return query.all()
    
    @staticmethod
    def get_course_enrollments(course_id, status=None):
        """获取课程的选课记录"""
        query = Enrollment.query.filter(Enrollment.course_id == course_id)
        if status:
            query = query.filter(Enrollment.status == status)
        return query.all()
