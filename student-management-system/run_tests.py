#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本
Test Runner Script
"""

import os
import sys
import pytest
import subprocess
from datetime import datetime

def run_unit_tests():
    """运行单元测试"""
    print("🧪 运行单元测试...")
    result = pytest.main([
        'tests/',
        '-v',
        '--tb=short',
        '--cov=models',
        '--cov=api',
        '--cov-report=html',
        '--cov-report=term-missing'
    ])
    return result == 0

def run_integration_tests():
    """运行集成测试"""
    print("🔗 运行集成测试...")
    result = pytest.main([
        'tests/test_api.py',
        '-v',
        '--tb=short',
        '-m', 'not slow'
    ])
    return result == 0

def run_performance_tests():
    """运行性能测试"""
    print("⚡ 运行性能测试...")
    # 这里可以添加性能测试的具体实现
    # 例如使用 locust 或 pytest-benchmark
    print("性能测试功能待实现")
    return True

def generate_test_report():
    """生成测试报告"""
    print("📊 生成测试报告...")
    
    # 创建报告目录
    report_dir = 'test_reports'
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    
    # 生成HTML测试报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f'{report_dir}/test_report_{timestamp}.html'
    
    result = pytest.main([
        'tests/',
        '--html=' + report_file,
        '--self-contained-html',
        '--tb=short'
    ])
    
    if result == 0:
        print(f"✅ 测试报告已生成: {report_file}")
    
    return result == 0

def check_code_quality():
    """检查代码质量"""
    print("🔍 检查代码质量...")
    
    try:
        # 使用 flake8 检查代码风格
        result = subprocess.run(['flake8', '.', '--max-line-length=120'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 代码风格检查通过")
        else:
            print("❌ 代码风格检查未通过:")
            print(result.stdout)
            return False
            
    except FileNotFoundError:
        print("⚠️  flake8 未安装，跳过代码风格检查")
    
    return True

def run_security_scan():
    """运行安全扫描"""
    print("🔒 运行安全扫描...")
    
    try:
        # 使用 bandit 进行安全扫描
        result = subprocess.run(['bandit', '-r', '.', '-f', 'json'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 安全扫描通过")
        else:
            print("⚠️  发现潜在安全问题，请检查报告")
            
    except FileNotFoundError:
        print("⚠️  bandit 未安装，跳过安全扫描")
    
    return True

def main():
    """主函数"""
    print("="*60)
    print("🎯 学生信息管理系统 - 测试套件")
    print("="*60)
    
    # 解析命令行参数
    test_type = sys.argv[1] if len(sys.argv) > 1 else 'all'
    
    success = True
    
    if test_type == 'unit' or test_type == 'all':
        success &= run_unit_tests()
    
    if test_type == 'integration' or test_type == 'all':
        success &= run_integration_tests()
    
    if test_type == 'performance' or test_type == 'all':
        success &= run_performance_tests()
    
    if test_type == 'quality' or test_type == 'all':
        success &= check_code_quality()
    
    if test_type == 'security' or test_type == 'all':
        success &= run_security_scan()
    
    if test_type == 'report':
        success &= generate_test_report()
    
    print("="*60)
    if success:
        print("✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败，请检查上述输出")
        sys.exit(1)

if __name__ == '__main__':
    main()
