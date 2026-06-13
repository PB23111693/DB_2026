from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            user.last_login = datetime.now()
            db.session.commit()
            flash(f'欢迎，{username}！', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('用户名或密码错误', 'danger')

    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """任何已登录用户均可修改自己的密码"""
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # 验证旧密码
        if not check_password_hash(current_user.password_hash, old_password):
            flash('旧密码错误', 'danger')
            return render_template('change_password.html')

        # 新密码一致性检查
        if new_password != confirm_password:
            flash('两次输入的新密码不一致', 'danger')
            return render_template('change_password.html')

        # 密码长度检查
        if len(new_password) < 6:
            flash('新密码长度至少为 6 位', 'danger')
            return render_template('change_password.html')

        # 更新密码
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        # 修改密码后强制重新登录
        logout_user()
        flash('密码修改成功，请使用新密码重新登录', 'success')
        return redirect(url_for('auth.login'))

    return render_template('change_password.html')