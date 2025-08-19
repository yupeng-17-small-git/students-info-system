# 学生信息管理系统

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)

一个基于 Flask 的现代化学生信息管理系统，提供学生管理、课程管理、图书借阅等核心功能。

## ✨ 主要特性

- 🎓 **学生信息管理** - 完整的学生档案管理和学籍状态跟踪
- 📚 **课程管理系统** - 课程创建、选课管理和成绩录入
- 📖 **图书借阅系统** - 图书库存管理和借还流程控制
- 📊 **数据统计分析** - 实时数据看板和趋势分析
- 🌐 **响应式界面** - 现代化Web界面，支持多设备访问
- 🔧 **RESTful API** - 完整的API接口，支持第三方集成
- 🧪 **高测试覆盖** - 完善的单元测试和集成测试

## 🛠 技术栈

### 后端技术
- **Python 3.8+** - 主要编程语言
- **Flask 2.3+** - Web应用框架
- **SQLAlchemy** - ORM数据库操作
- **Flask-RESTful** - RESTful API构建
- **SQLite/PostgreSQL** - 数据库存储

### 前端技术
- **Bootstrap 5** - UI组件库
- **jQuery 3.7** - JavaScript库
- **Font Awesome** - 图标库
- **响应式设计** - 支持多设备访问

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- pip 包管理器
- 现代浏览器 (Chrome, Firefox, Safari, Edge)

### 安装步骤

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **初始化数据库**
   ```bash
   python app.py --init-db
   ```

3. **启动应用**
   ```bash
   python app.py --port 5000
   ```

4. **访问应用**
   - 管理后台: http://localhost:5000
   - API接口: http://localhost:5000/api

## 📖 功能介绍

### 1. 学生信息管理
- 学生档案的增删改查
- 支持批量导入和搜索
- 学籍状态管理
- 联系方式维护

### 2. 课程管理
- 课程信息维护
- 开课计划安排
- 选课人数限制
- 课程状态控制

### 3. 选课系统
- 学生在线选课
- 退课申请处理
- 成绩录入管理
- 选课统计分析

### 4. 图书借阅
- 图书信息管理
- 借阅归还流程
- 逾期提醒功能
- 罚金计算处理

### 5. 数据统计
- 实时数据看板
- 学生分布统计
- 热门课程排行
- 借阅趋势分析

## 🧪 运行测试

```bash
# 运行所有测试
python run_tests.py

# 运行单元测试
python run_tests.py unit

# 运行API测试
python run_tests.py integration
```

## 📊 项目结构

```
student-management-system/
├── app.py                 # 主应用文件
├── config.py             # 配置文件
├── requirements.txt      # 依赖包列表
├── models/              # 数据模型
├── api/                 # API接口
├── views/               # Web视图
├── templates/           # HTML模板
├── static/              # 静态资源
├── tests/               # 测试文件
└── docs/                # 文档
```

## 🔧 配置说明

### 数据库配置

**开发环境（SQLite）**
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///student_management.db'
```

**生产环境（PostgreSQL）**
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/dbname'
```

## 🚀 部署指南

### 使用 Gunicorn 部署

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支
3. 提交更改
4. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证

## 📞 联系方式

- 项目维护者：Assistant
- 创建日期：2025-08-15

---

**感谢使用学生信息管理系统！** 🎓
