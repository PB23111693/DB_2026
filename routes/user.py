from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from werkzeug.security import generate_password_hash
from models import db, User, Department, Course
from routes import admin_required

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/')
@login_required
@admin_required
def list():
    role = request.args.get('role')
    if role == 'teacher':
        users = User.query.filter_by(role='teacher').all()
        page_title = '教师管理'
        teacher_data = []
        for u in users:
            courses = Course.query.filter_by(teacher_id=u.related_id).all()
            teacher_data.append({'user': u, 'courses': courses, 'course_count': len(courses)})
        return render_template('user/list.html', teacher_data=teacher_data,
                               users=users, departments=Department.query.all(),
                               page_title=page_title, role=role)
    elif role == 'student':
        users = User.query.filter_by(role='student').all()
        page_title = '学生账号管理'
        return render_template('user/list.html', users=users, departments=Department.query.all(),
                               page_title=page_title, role=role)
    else:
        users = User.query.all()
        page_title = '用户管理'
        return render_template('user/list.html', users=users, departments=Department.query.all(),
                               page_title=page_title, role=role)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    preselected_role = request.args.get('role', '')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role') or preselected_role or 'student'
        related_id = request.form.get('related_id') or None
        name = request.form.get('name') or None
        dept_id = request.form.get('dept_id') or None

        # 检查用户名唯一性
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return render_template('user/form.html', user=None, departments=Department.query.all(),
                                   preselected_role=preselected_role)

        # 检查工号/学号唯一性（仅限学生和教师角色）
        if role in ('teacher', 'student') and related_id:
            existing = User.query.filter_by(role=role, related_id=related_id).first()
            if existing:
                flash(f'该{"学号" if role == "student" else "工号"} {related_id} 已被用户 {existing.username} 使用', 'danger')
                return render_template('user/form.html', user=None, departments=Department.query.all(),
                                       preselected_role=preselected_role)

        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role=role,
            name=name,
            dept_id=dept_id,
            related_id=related_id
        )
        db.session.add(user)
        db.session.commit()
        flash('用户添加成功', 'success')
        if role == 'teacher':
            return redirect(url_for('user.list', role='teacher'))
        elif role == 'student':
            return redirect(url_for('user.list', role='student'))
        else:
            return redirect(url_for('user.list'))

    departments = Department.query.all()
    return render_template('user/form.html', user=None, departments=departments, preselected_role=preselected_role)

@bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(user_id):
    user = User.query.get_or_404(user_id)
    departments = Department.query.all()
    admin_count = User.query.filter_by(role='admin').count()
    is_last_admin = (user.role == 'admin' and admin_count <= 1)

    if request.method == 'POST':
        new_role = request.form['role']
        if user.role == 'admin' and new_role != 'admin' and admin_count <= 1:
            flash('不允许修改唯一的管理员角色！请先添加其他管理员。', 'danger')
            return render_template('user/form.html', user=user, departments=departments, is_last_admin=True)

        new_related_id = request.form.get('related_id') or None
        # 工号/学号唯一性检查（排除自身）
        if new_role in ('teacher', 'student') and new_related_id:
            existing = User.query.filter(User.role == new_role, User.related_id == new_related_id, User.user_id != user.user_id).first()
            if existing:
                flash(f'该{"学号" if new_role == "student" else "工号"} {new_related_id} 已被用户 {existing.username} 使用', 'danger')
                return render_template('user/form.html', user=user, departments=departments, is_last_admin=is_last_admin)

        user.username = request.form['username']
        if request.form.get('password'):
            user.password_hash = generate_password_hash(request.form['password'])
        user.role = new_role
        user.name = request.form.get('name') or None
        user.dept_id = request.form.get('dept_id') or None
        user.related_id = new_related_id
        db.session.commit()

        if user.user_id == current_user.user_id and new_role != current_user.role:
            logout_user()
            flash('您的角色已变更，请使用新角色重新登录。', 'info')
            return redirect(url_for('auth.login'))

        flash('用户更新成功', 'success')
        return redirect(url_for('user.list', role=user.role if user.role != 'admin' else None))

    return render_template('user/form.html', user=user, departments=departments, is_last_admin=is_last_admin)

@bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin' and User.query.filter_by(role='admin').count() <= 1:
        flash('不能删除唯一的管理员账户', 'danger')
        return redirect(url_for('user.list'))

    if user.role == 'teacher':
        Course.query.filter_by(teacher_id=user.related_id).update({Course.teacher_id: None})
        db.session.flush()

    db.session.delete(user)
    db.session.commit()
    flash('用户已删除，若为教师已解除所有课程关联', 'info')
    return redirect(url_for('user.list', role=user.role if user.role != 'admin' else None))