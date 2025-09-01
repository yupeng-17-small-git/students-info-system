#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生管理系统启动脚本
Student Management System Startup Script

完整的系统启动和初始化脚本
"""

import os
import sys
import argparse
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_available_port():
    """获取可用端口"""
    import socket
    
    # 常用端口列表
    preferred_ports = [5000, 8000, 8080, 3000, 5001, 8001]
    
    for port in preferred_ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return port
            except OSError:
                continue
    
    # 如果常用端口都被占用，使用系统分配
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 0))
        return s.getsockname()[1]

def start_application(port=None, debug=False):
    """启动应用"""
    print("🚀 启动学生管理系统...")
    
    try:
        # 设置环境变量
        os.environ['PYTHONPATH'] = '/home/ubuntu/.local/lib/python3.10/site-packages:' + os.environ.get('PYTHONPATH', '')
        
        from app import create_app
        from config import DevelopmentConfig, ProductionConfig
        
        # 选择配置
        config = DevelopmentConfig if debug else ProductionConfig
        app = create_app(config)
        
        # 获取端口
        if port is None:
            port = get_available_port()
        
        print(f"\n" + "="*60)
        print(f"🎉 学生管理系统启动成功！")
        print(f"="*60)
        print(f"🌐 Web界面: http://localhost:{port}")
        print(f"📊 管理后台: http://localhost:{port}/dashboard")
        print(f"🔌 API接口: http://localhost:{port}/api")
        print(f"📝 模式: {'开发模式' if debug else '生产模式'}")
        print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"="*60)
        print(f"💡 使用说明:")
        print(f"   • 访问 /dashboard 查看系统概况")
        print(f"   • 访问 /students 管理学生信息")
        print(f"   • 访问 /courses 管理课程信息")
        print(f"   • 访问 /books 管理图书信息")
        print(f"   • 使用 Ctrl+C 停止服务")
        print(f"="*60)
        
        # 启动Flask应用
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug,
            use_reloader=False
        )
        
        return True
        
    except Exception as e:
        print(f"❌ 应用启动失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='学生管理系统启动脚本')
    parser.add_argument('--port', type=int, help='指定服务器端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    print("="*70)
    print("🎯 学生管理系统 - 启动脚本")
    print("="*70)
    print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python版本: {sys.version.split()[0]}")
    
    # 启动应用
    return start_application(port=args.port, debug=args.debug)

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 系统已停止运行，感谢使用学生管理系统！")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 启动脚本异常: {e}")
        sys.exit(1)
