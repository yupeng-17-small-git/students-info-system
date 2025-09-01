#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合测试运行器
Comprehensive Test Runner

运行所有测试并生成详细报告
"""

import sys
import os
import subprocess
import json
from datetime import datetime

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd,
            timeout=300
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "命令执行超时"
    except Exception as e:
        return 1, "", str(e)

def generate_test_report():
    """生成测试报告"""
    print("\n" + "="*60)
    print("🧪 学生管理系统 - 综合测试报告")
    print("="*60)
    print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python版本: {sys.version}")
    
    # 检查测试环境
    print("\n🔧 测试环境检查...")
    
    # 检查依赖
    dependencies = ['flask', 'pytest', 'sqlalchemy']
    for dep in dependencies:
        returncode, stdout, stderr = run_command(f"python3 -c 'import {dep}; print({dep}.__version__)'")
        if returncode == 0:
            print(f"  ✅ {dep}: {stdout.strip()}")
        else:
            print(f"  ❌ {dep}: 未安装")
            return False
    
    # 运行测试
    test_results = {}
    
    # 1. Bug修复测试
    print("\n🐛 运行Bug修复测试...")
    returncode, stdout, stderr = run_command(
        "PYTHONPATH=/home/ubuntu/.local/lib/python3.10/site-packages:$PYTHONPATH python3 -m pytest tests/test_bug_fixes.py -v --tb=short",
        cwd="."
    )
    test_results['bug_fixes'] = {
        'returncode': returncode,
        'output': stdout if returncode == 0 else stderr
    }
    
    if returncode == 0:
        print("  ✅ Bug修复测试通过")
    else:
        print("  ❌ Bug修复测试失败")
        print(f"     错误信息: {stderr[:200]}..." if len(stderr) > 200 else stderr)
    
    # 2. 视图层测试
    print("\n🖼️  运行视图层测试...")
    returncode, stdout, stderr = run_command(
        "PYTHONPATH=/home/ubuntu/.local/lib/python3.10/site-packages:$PYTHONPATH python3 -m pytest tests/test_views.py -v --tb=short",
        cwd="."
    )
    test_results['views'] = {
        'returncode': returncode,
        'output': stdout if returncode == 0 else stderr
    }
    
    if returncode == 0:
        print("  ✅ 视图层测试通过")
    else:
        print("  ❌ 视图层测试失败")
    
    # 3. API测试
    print("\n🌐 运行API测试...")
    returncode, stdout, stderr = run_command(
        "PYTHONPATH=/home/ubuntu/.local/lib/python3.10/site-packages:$PYTHONPATH python3 -m pytest tests/test_api_complete.py -v --tb=short",
        cwd="."
    )
    test_results['api'] = {
        'returncode': returncode,
        'output': stdout if returncode == 0 else stderr
    }
    
    if returncode == 0:
        print("  ✅ API测试通过")
    else:
        print("  ❌ API测试失败")
    
    # 4. 边界情况测试
    print("\n⚠️  运行边界情况测试...")
    returncode, stdout, stderr = run_command(
        "PYTHONPATH=/home/ubuntu/.local/lib/python3.10/site-packages:$PYTHONPATH python3 -m pytest tests/test_edge_cases.py -v --tb=short",
        cwd="."
    )
    test_results['edge_cases'] = {
        'returncode': returncode,
        'output': stdout if returncode == 0 else stderr
    }
    
    if returncode == 0:
        print("  ✅ 边界情况测试通过")
    else:
        print("  ❌ 边界情况测试失败")
    
    # 5. 原有模型测试
    print("\n📊 运行原有模型测试...")
    returncode, stdout, stderr = run_command(
        "PYTHONPATH=/home/ubuntu/.local/lib/python3.10/site-packages:$PYTHONPATH python3 -m pytest tests/test_models.py -v --tb=short",
        cwd="."
    )
    test_results['models'] = {
        'returncode': returncode,
        'output': stdout if returncode == 0 else stderr
    }
    
    if returncode == 0:
        print("  ✅ 原有模型测试通过")
    else:
        print("  ❌ 原有模型测试失败")
    
    # 生成总结报告
    print("\n📋 测试总结:")
    passed_tests = sum(1 for result in test_results.values() if result['returncode'] == 0)
    total_tests = len(test_results)
    
    print(f"  总测试套件: {total_tests}")
    print(f"  通过测试: {passed_tests}")
    print(f"  失败测试: {total_tests - passed_tests}")
    print(f"  成功率: {passed_tests/total_tests*100:.1f}%")
    
    # 保存详细报告
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total': total_tests,
            'passed': passed_tests,
            'failed': total_tests - passed_tests,
            'success_rate': passed_tests/total_tests*100
        },
        'results': test_results
    }
    
    with open('test_report.json', 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细报告已保存到: test_report.json")
    
    if passed_tests == total_tests:
        print("\n🎉 所有测试通过！系统Bug已修复！")
        return True
    else:
        print("\n⚠️  仍有测试失败，需要进一步修复")
        return False

if __name__ == '__main__':
    success = generate_test_report()
    sys.exit(0 if success else 1)
