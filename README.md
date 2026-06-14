
# 学籍管理系统

> 2026春数据库系统及应用课程设计 —— 一个完整的 B/S 架构学籍管理平台

## 📖 项目简介

本系统针对高校学籍管理的典型业务场景，实现了学生基本信息维护、专业变更、奖惩记录、课程管理、成绩录入与统计分析、PDF成绩单导出等功能。系统支持 **管理员、教师、学生** 三种角色，不同角色具有严格的权限控制。数据库采用 MySQL，后端基于 Python Flask，前端使用 Bootstrap 5，整体架构清晰，易于部署和扩展。

## ✨ 主要功能

- **学生管理**：学生信息的增删改查，支持照片、简历等文件上传/预览
- **教师管理**：管理员可维护教师信息，教师可查看自己所授课程及学生名单
- **选课管理**：管理员统一排课，学生可自主选课/退选（已出成绩的课程不能退选）
- **成绩管理**：教师录入成绩（仅限本人课程），支持部分字段更新、绩点自动计算、统计分析（平均分、排名）和 PDF 成绩单导出
- **专业变更**：通过存储过程实现带事务回滚的专业变更，并记录历史
- **奖惩管理**：记录奖励/处罚信息，并利用触发器自动标记处分状态
- **文件管理**：统一上传、类型过滤、安全清理
- **高级数据库特性**：存储过程、函数、触发器、事务一应俱全，满足课程实验要求

## 🛠 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | HTML5, CSS3, Bootstrap 5, Jinja2 |
| 后端 | Python 3.10+, Flask, Flask-Login |
| ORM | SQLAlchemy |
| 数据库 | MySQL 8.0 (存储过程/函数/触发器/事务) |
| 文件处理 | Pillow (图片缩略图), ReportLab (PDF) |
| 安全 | Werkzeug 密码哈希, 上传白名单 |

采用 **B/S 架构**，用户通过浏览器访问，前端模板由 Jinja2 渲染，后端核心业务逻辑封装在路由和数据库对象中，实现了清晰的层次分离。

## 🚀 快速开始

### 环境要求

- Python 3.10+
- MySQL 8.0+
- Git (可选)
- 中文字体文件 `SimSun.ttf`（用于 PDF 成绩单，需自行放入 `static/fonts/` 目录）

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/PB23111693/DB_2026.git
   cd DB_2026
   ```

2. **创建虚拟环境（推荐）**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/macOS
   venv\Scripts\activate      # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置数据库**
   - 打开 `config.py`，修改数据库连接字符串中的用户名、密码和数据库名（默认数据库名为 `xueji_db`）。
   - 在 MySQL 中运行初始化脚本：
     ```bash
     mysql -u root -p < init_db.sql
     ```
   - 该脚本会自动创建数据库、表、触发器、存储过程并插入示例数据。

5. **准备中文字体**
   - 下载宋体字体文件，重命名为 `SimSun.ttf`，放入 `static/fonts/` 目录（若没有，PDF 中可能乱码，但不影响其他功能）。

6. **启动应用**
   ```bash
   python app.py
   ```
   访问 `http://127.0.0.1:5000` 即可打开系统。

### 默认账户

| 角色   | 用户名 | 密码   |
|--------|--------|--------|
| 管理员 | admin  | 123456 |
| 教师   | teacher_zhang | 123456 (或其他由脚本创建的教师) |
| 学生   | 2024001 | 123456 (或其他学号对应的学生) |

> 所有由初始化脚本创建的用户，初始密码均为 `123456`。管理员可在“用户管理”界面修改或重置密码。

## 📁 目录结构

```
DB_2026/
├── app.py                 # Flask 主应用
├── config.py              # 配置文件
├── models.py              # 数据模型
├── init_db.sql            # 数据库初始化脚本（建表、触发器、存储过程）
├── requirements.txt       # Python 依赖
├── import_scores.py       # 批量导入成绩示例脚本
├── routes/                # 路由模块（蓝图）
│   ├── __init__.py        # 权限装饰器
│   ├── auth.py            # 登录/登出/修改密码
│   ├── student.py         # 学生管理、选课
│   ├── course.py          # 课程管理
│   ├── score.py           # 成绩管理、统计、PDF导出
│   ├── major_change.py    # 专业变更
│   ├── award.py           # 奖励与处罚
│   ├── user.py            # 用户管理
│   ├── base_data.py       # 院系/专业/班级管理
│   ├── teacher.py         # 教师工作台
│   ├── enrollment_admin.py# 选课管理（管理员）
│   └── upload.py          # 文件上传与访问
├── services/              # 服务层
│   ├── file_service.py    # 文件存储/清理
│   └── pdf_service.py     # PDF 成绩单生成
├── templates/             # Jinja2 模板
│   ├── base.html          # 基础布局
│   ├── index.html         # 首页
│   ├── login.html         # 登录页
│   ├── change_password.html
│   ├── student/           # 学生相关模板
│   ├── course/            # 课程相关模板
│   ├── score/             # 成绩相关模板
│   ├── teacher/           # 教师端模板
│   ├── department/        # 院系模板
│   ├── major/             # 专业模板
│   ├── class/             # 班级模板
│   ├── enrollment_admin/  # 选课管理模板
│   └── user/              # 用户管理模板
└── static/                # 静态资源
    ├── uploads/           # 上传文件存储
    └── fonts/             # 字体文件（SimSun.ttf）
```
