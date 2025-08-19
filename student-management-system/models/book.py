#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图书模型
Book Model
"""

from datetime import datetime
from . import db

class Book(db.Model):
    """图书模型类"""
    __tablename__ = 'books'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 基本信息
    isbn = db.Column(db.String(20), unique=True, nullable=False, comment='ISBN号')
    title = db.Column(db.String(200), nullable=False, comment='书名')
    author = db.Column(db.String(100), nullable=False, comment='作者')
    publisher = db.Column(db.String(100), nullable=False, comment='出版社')
    publish_date = db.Column(db.Date, comment='出版日期')
    
    # 分类信息
    category = db.Column(db.String(50), comment='图书分类')
    tags = db.Column(db.String(200), comment='标签')
    
    # 物理信息
    total_copies = db.Column(db.Integer, default=1, nullable=False, comment='总册数')
    location = db.Column(db.String(50), comment='存放位置')
    
    # 详细信息
    description = db.Column(db.Text, comment='图书描述')
    pages = db.Column(db.Integer, comment='页数')
    language = db.Column(db.String(20), default='中文', comment='语言')
    
    # 状态信息
    status = db.Column(db.String(20), default='available', comment='状态：available-可借，unavailable-不可借')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    borrow_records = db.relationship('BorrowRecord', back_populates='book', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Book, self).__init__(**kwargs)
    
    def __repr__(self):
        return f'<Book {self.isbn}: {self.title}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'publisher': self.publisher,
            'publish_date': self.publish_date.isoformat() if self.publish_date else None,
            'category': self.category,
            'tags': self.tags,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'borrowed_copies': self.borrowed_copies,
            'location': self.location,
            'description': self.description,
            'pages': self.pages,
            'language': self.language,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create(cls, **kwargs):
        """创建图书记录"""
        book = cls(**kwargs)
        db.session.add(book)
        db.session.commit()
        return book
    
    def update(self, **kwargs):
        """更新图书信息"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
    
    def delete(self):
        """删除图书记录"""
        db.session.delete(self)
        db.session.commit()
    
    @property
    def borrowed_copies(self):
        """已借出册数"""
        from .borrow_record import BorrowRecord
        return BorrowRecord.query.filter(
            BorrowRecord.book_id == self.id,
            BorrowRecord.status == 'borrowed'
        ).count()
    
    @property
    def available_copies(self):
        """可借册数"""
        return self.total_copies - self.borrowed_copies
    
    def can_borrow(self):
        """检查是否可以借阅"""
        return (
            self.status == 'available' and 
            self.available_copies > 0
        )
    
    @property
    def current_borrowers(self):
        """当前借阅者"""
        from .student import Student
        return db.session.query(Student).join(BorrowRecord).filter(
            BorrowRecord.book_id == self.id,
            BorrowRecord.status == 'borrowed'
        ).all()
    
    @staticmethod
    def search(keyword, page=1, per_page=10):
        """搜索图书"""
        query = Book.query.filter(
            db.or_(
                Book.isbn.contains(keyword),
                Book.title.contains(keyword),
                Book.author.contains(keyword),
                Book.publisher.contains(keyword),
                Book.category.contains(keyword)
            )
        )
        return query.paginate(
            page=page, per_page=per_page, error_out=False
        )
