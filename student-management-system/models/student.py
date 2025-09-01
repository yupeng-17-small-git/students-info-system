#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生模型
Student Model
"""

from datetime import datetime
from . import db
from sqlalchemy import func

class Student(db.Model):
    """学生模型类"""
    __tablename__ = 'students'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 基本信息
    student_id = db.Column(db.String(20), unique=True, nullable=False, comment='学号')
    name = db.Column(db.String(50), nullable=False, comment='姓名')
    id_card = db.Column(db.String(18), unique=True, nullable=False, comment='身份证号')
    gender = db.Column(db.String(10), nullable=False, comment='性别')
    age = db.Column(db.Integer, nullable=False, comment='年龄')
    
    # 学籍信息
    major = db.Column(db.String(100), nullable=False, comment='专业')
    grade = db.Column(db.String(10), nullable=False, comment='年级')
    class_name = db.Column(db.String(50), comment='班级')
    
    # 联系方式
    email = db.Column(db.String(120), unique=True, comment='邮箱')
    phone = db.Column(db.String(20), comment='电话')
    address = db.Column(db.Text, comment='地址')
    
    # 状态信息
    status = db.Column(db.String(20), default='active', comment='状态：active-在读，graduated-已毕业，suspended-休学')
    enrollment_date = db.Column(db.Date, default=lambda: datetime.utcnow().date(), comment='入学日期')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    enrollments = db.relationship('Enrollment', back_populates='student', cascade='all, delete-orphan')
    borrow_records = db.relationship('BorrowRecord', back_populates='student', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Student, self).__init__(**kwargs)
    
    def __repr__(self):
        return f'<Student {self.student_id}: {self.name}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'id_card': self.id_card,
            'gender': self.gender,
            'age': self.age,
            'major': self.major,
            'grade': self.grade,
            'class_name': self.class_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'status': self.status,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create(cls, **kwargs):
        """创建学生记录"""
        student = cls(**kwargs)
        db.session.add(student)
        db.session.commit()
        return student
    
    def update(self, **kwargs):
        """更新学生信息"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
    
    def delete(self):
        """删除学生记录"""
        db.session.delete(self)
        db.session.commit()
    
    @property
    def enrolled_courses(self):
        """获取已选课程"""
        from .course import Course
        return db.session.query(Course).join(Enrollment).filter(
            Enrollment.student_id == self.id,
            Enrollment.status == 'enrolled'
        ).all()
    
    @property
    def borrowed_books(self):
        """获取已借图书"""
        from .book import Book
        return db.session.query(Book).join(BorrowRecord).filter(
            BorrowRecord.student_id == self.id,
            BorrowRecord.status == 'borrowed'
        ).all()
    
    @staticmethod
    def search(keyword, page=1, per_page=10):
        """搜索学生"""
        query = Student.query.filter(
            db.or_(
                Student.student_id.contains(keyword),
                Student.name.contains(keyword),
                Student.major.contains(keyword),
                Student.grade.contains(keyword)
            )
        )
        return query.paginate(
            page=page, per_page=per_page, error_out=False
        )

    def validate_age(self):
        """验证年龄"""
        if self.age is not None:
            if self.age < 0 or self.age > 150:
                raise ValueError("年龄必须在0-150之间")
    
    def validate_id_card(self):
        """验证身份证号"""
        if self.id_card:
            # 简单的身份证号验证
            if len(self.id_card) not in [15, 18]:
                raise ValueError("身份证号长度不正确")
            
            # 检查是否全为数字（除了最后一位可能是X）
            if not (self.id_card[:-1].isdigit() and 
                   (self.id_card[-1].isdigit() or self.id_card[-1].upper() == 'X')):
                raise ValueError("身份证号格式不正确")
    
    def validate_student_id(self):
        """验证学号"""
        if not self.student_id or len(self.student_id.strip()) == 0:
            raise ValueError("学号不能为空")
    
    def validate_name(self):
        """验证姓名"""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("姓名不能为空")
        if len(self.name) > 50:
            raise ValueError("姓名长度不能超过50个字符")
    
    def validate(self):
        """执行所有验证"""
        self.validate_name()
        self.validate_student_id()
        self.validate_age()
        self.validate_id_card()
