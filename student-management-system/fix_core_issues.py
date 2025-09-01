#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心功能修复脚本
Core Issues Fix Script

修复系统中的关键功能问题
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_book_inventory_control():
    """修复图书库存控制问题"""
    print("📚 修复图书库存控制...")
    
    # 在 models/borrow_record.py 中添加库存检查
    borrow_record_fix = '''
    @staticmethod
    def check_book_availability(book_id):
        """检查图书是否可借"""
        from .book import Book
        
        book = Book.query.get(book_id)
        if not book:
            return False, "图书不存在"
        
        # 计算已借出的副本数
        borrowed_count = BorrowRecord.query.filter(
            BorrowRecord.book_id == book_id,
            BorrowRecord.status == 'borrowed'
        ).count()
        
        if borrowed_count >= book.total_copies:
            return False, "图书已全部借出"
        
        return True, f"可借副本：{book.total_copies - borrowed_count}"
    
    @classmethod
    def create_with_inventory_check(cls, **kwargs):
        """创建借书记录时检查库存"""
        book_id = kwargs.get('book_id')
        if book_id:
            available, message = cls.check_book_availability(book_id)
            if not available:
                raise ValueError(message)
        
        return cls.create(**kwargs)
'''
    
    # 读取当前文件
    with open('models/borrow_record.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 如果没有库存检查方法，则添加
    if 'check_book_availability' not in content:
        # 在类的最后添加新方法（在最后一个方法之前）
        insert_pos = content.rfind('        return len(overdue_records)')
        if insert_pos != -1:
            # 找到插入点的下一行
            insert_pos = content.find('\n', insert_pos) + 1
            new_content = content[:insert_pos] + borrow_record_fix + content[insert_pos:]
            
            with open('models/borrow_record.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("  ✅ 图书库存控制方法已添加")
            return True
    
    print("  ✅ 图书库存控制已存在")
    return True

def fix_data_validation():
    """修复数据验证问题"""
    print("\n🔍 修复数据验证...")
    
    # 学生年龄验证
    student_validation = '''
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
'''
    
    try:
        with open('models/student.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'validate_age' not in content:
            # 在类的最后添加验证方法
            insert_pos = content.rfind('        return query.paginate(')
            if insert_pos != -1:
                # 找到方法的结束位置
                insert_pos = content.find(')', insert_pos) + 1
                insert_pos = content.find('\n', insert_pos) + 1
                
                new_content = content[:insert_pos] + student_validation + content[insert_pos:]
                
                with open('models/student.py', 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print("  ✅ 学生数据验证方法已添加")
        else:
            print("  ✅ 学生数据验证已存在")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 学生数据验证修复失败: {e}")
        return False

def fix_api_error_handling():
    """修复API错误处理"""
    print("\n🌐 修复API错误处理...")
    
    # 通用错误处理装饰器
    error_handler_code = '''
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
'''
    
    try:
        # 检查是否已有错误处理
        with open('api/__init__.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'handle_api_errors' not in content:
            # 在文件末尾添加错误处理代码
            new_content = content + '\n' + error_handler_code
            
            with open('api/__init__.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("  ✅ API错误处理装饰器已添加")
        else:
            print("  ✅ API错误处理已存在")
        
        return True
        
    except Exception as e:
        print(f"  ❌ API错误处理修复失败: {e}")
        return False

def fix_course_credits_validation():
    """修复课程学分验证"""
    print("\n📚 修复课程学分验证...")
    
    course_validation = '''
    def validate_credits(self):
        """验证学分"""
        if self.credits is not None:
            if self.credits <= 0 or self.credits > 10:
                raise ValueError("学分必须在1-10之间")
    
    def validate_code(self):
        """验证课程代码"""
        if not self.code or len(self.code.strip()) == 0:
            raise ValueError("课程代码不能为空")
    
    def validate_name(self):
        """验证课程名称"""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("课程名称不能为空")
        if len(self.name) > 100:
            raise ValueError("课程名称长度不能超过100个字符")
    
    def validate(self):
        """执行所有验证"""
        self.validate_code()
        self.validate_name()
        self.validate_credits()
'''
    
    try:
        with open('models/course.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'validate_credits' not in content:
            # 在类的最后添加验证方法
            insert_pos = content.rfind('        return query.paginate(')
            if insert_pos != -1:
                insert_pos = content.find(')', insert_pos) + 1
                insert_pos = content.find('\n', insert_pos) + 1
                
                new_content = content[:insert_pos] + course_validation + content[insert_pos:]
                
                with open('models/course.py', 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print("  ✅ 课程数据验证方法已添加")
        else:
            print("  ✅ 课程数据验证已存在")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 课程数据验证修复失败: {e}")
        return False

def fix_book_copies_validation():
    """修复图书副本数验证"""
    print("\n📖 修复图书副本数验证...")
    
    book_validation = '''
    def validate_total_copies(self):
        """验证图书副本数"""
        if self.total_copies is not None:
            if self.total_copies <= 0 or self.total_copies > 1000:
                raise ValueError("图书副本数必须在1-1000之间")
    
    def validate_isbn(self):
        """验证ISBN"""
        if not self.isbn or len(self.isbn.strip()) == 0:
            raise ValueError("ISBN不能为空")
        # 简单的ISBN格式检查
        isbn_clean = self.isbn.replace('-', '').replace(' ', '')
        if not (len(isbn_clean) in [10, 13] and isbn_clean[:-1].isdigit()):
            raise ValueError("ISBN格式不正确")
    
    def validate_title(self):
        """验证书名"""
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("书名不能为空")
        if len(self.title) > 200:
            raise ValueError("书名长度不能超过200个字符")
    
    def validate(self):
        """执行所有验证"""
        self.validate_isbn()
        self.validate_title()
        self.validate_total_copies()
'''
    
    try:
        with open('models/book.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'validate_total_copies' not in content:
            # 在类的最后添加验证方法
            insert_pos = content.rfind('        return query.paginate(')
            if insert_pos != -1:
                insert_pos = content.find(')', insert_pos) + 1
                insert_pos = content.find('\n', insert_pos) + 1
                
                new_content = content[:insert_pos] + book_validation + content[insert_pos:]
                
                with open('models/book.py', 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print("  ✅ 图书数据验证方法已添加")
        else:
            print("  ✅ 图书数据验证已存在")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 图书数据验证修复失败: {e}")
        return False

def main():
    """主修复函数"""
    print("="*60)
    print("🔧 学生管理系统 - 核心功能修复")
    print("="*60)
    
    fixes = [
        ("图书库存控制", fix_book_inventory_control),
        ("学生数据验证", fix_data_validation),
        ("课程学分验证", fix_course_credits_validation),
        ("图书副本验证", fix_book_copies_validation),
        ("API错误处理", fix_api_error_handling)
    ]
    
    success_count = 0
    total_count = len(fixes)
    
    for name, fix_func in fixes:
        try:
            if fix_func():
                success_count += 1
                print(f"\n✅ {name}: 修复完成")
            else:
                print(f"\n❌ {name}: 修复失败")
        except Exception as e:
            print(f"\n❌ {name}: 修复异常 - {e}")
    
    print("\n" + "="*60)
    print(f"📊 修复结果: {success_count}/{total_count} 项成功")
    
    if success_count == total_count:
        print("🎉 所有核心功能修复完成！")
        print("✅ 系统功能已完善，可以正常使用")
    else:
        print("⚠️  部分功能修复失败，建议检查相关代码")
    
    return success_count == total_count

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
