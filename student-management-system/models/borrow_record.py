#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
借书记录模型
Borrow Record Model
"""

from datetime import datetime, timedelta
from . import db

class BorrowRecord(db.Model):
    """借书记录模型类"""
    __tablename__ = 'borrow_records'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 外键关联
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, comment='学生ID')
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False, comment='图书ID')
    
    # 借阅信息
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow, comment='借阅日期')
    due_date = db.Column(db.DateTime, comment='应还日期')
    return_date = db.Column(db.DateTime, comment='实际还书日期')
    
    # 状态信息
    status = db.Column(db.String(20), default='borrowed', comment='状态：borrowed-已借出，returned-已归还，overdue-逾期，lost-丢失')
    
    # 费用信息
    fine_amount = db.Column(db.Float, default=0.0, comment='罚金金额')
    fine_paid = db.Column(db.Boolean, default=False, comment='罚金是否已付')
    
    # 备注信息
    notes = db.Column(db.Text, comment='备注')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    student = db.relationship('Student', back_populates='borrow_records')
    book = db.relationship('Book', back_populates='borrow_records')
    
    def __init__(self, **kwargs):
        super(BorrowRecord, self).__init__(**kwargs)
        # 设置默认归还日期（借阅后30天）
        if not self.due_date:
            self.due_date = self.borrow_date + timedelta(days=30)
    
    def __repr__(self):
        return f'<BorrowRecord Student:{self.student_id} Book:{self.book_id}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'book_id': self.book_id,
            'student_name': self.student.name if self.student else None,
            'student_student_id': self.student.student_id if self.student else None,
            'book_title': self.book.title if self.book else None,
            'book_isbn': self.book.isbn if self.book else None,
            'borrow_date': self.borrow_date.isoformat() if self.borrow_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'status': self.status,
            'is_overdue': self.is_overdue,
            'days_overdue': self.days_overdue,
            'fine_amount': self.fine_amount,
            'fine_paid': self.fine_paid,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create(cls, **kwargs):
        """创建借书记录"""
        record = cls(**kwargs)
        db.session.add(record)
        db.session.commit()
        return record
    
    def update(self, **kwargs):
        """更新借书记录"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
    
    def delete(self):
        """删除借书记录"""
        db.session.delete(self)
        db.session.commit()
    
    @property
    def is_overdue(self):
        """是否逾期"""
        if self.status == 'returned':
            return False
        return datetime.utcnow() > self.due_date
    
    @property
    def days_overdue(self):
        """逾期天数"""
        if not self.is_overdue:
            return 0
        return (datetime.utcnow() - self.due_date).days
    
    def return_book(self, fine_amount=None):
        """归还图书"""
        self.return_date = datetime.utcnow()
        self.status = 'returned'
        
        # 计算罚金
        if self.is_overdue and fine_amount is None:
            # 每天1元罚金
            self.fine_amount = self.days_overdue * 1.0
        elif fine_amount is not None:
            self.fine_amount = fine_amount
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
    
    def mark_lost(self, fine_amount=None):
        """标记为丢失"""
        self.status = 'lost'
        if fine_amount is not None:
            self.fine_amount = fine_amount
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
    
    def pay_fine(self):
        """支付罚金"""
        self.fine_paid = True
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
    
    def extend_due_date(self, days=7):
        """延长归还日期"""
        self.due_date = self.due_date + timedelta(days=days)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
    
    @staticmethod
    def get_by_student_and_book(student_id, book_id):
        """根据学生和图书获取借阅记录"""
        return BorrowRecord.query.filter(
            BorrowRecord.student_id == student_id,
            BorrowRecord.book_id == book_id,
            BorrowRecord.status == 'borrowed'
        ).first()
    
    @staticmethod
    def get_student_borrows(student_id, status=None):
        """获取学生的借阅记录"""
        query = BorrowRecord.query.filter(BorrowRecord.student_id == student_id)
        if status:
            query = query.filter(BorrowRecord.status == status)
        return query.all()
    
    @staticmethod
    def get_book_borrows(book_id, status=None):
        """获取图书的借阅记录"""
        query = BorrowRecord.query.filter(BorrowRecord.book_id == book_id)
        if status:
            query = query.filter(BorrowRecord.status == status)
        return query.all()
    
    @staticmethod
    def get_overdue_records():
        """获取所有逾期记录"""
        return BorrowRecord.query.filter(
            BorrowRecord.status == 'borrowed',
            BorrowRecord.due_date < datetime.utcnow()
        ).all()
    
    @classmethod
    def update_overdue_status(cls):
        """更新逾期状态"""
        overdue_records = cls.get_overdue_records()
        for record in overdue_records:
            record.status = 'overdue'
        db.session.commit()
        return len(overdue_records)
