from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Department, Major, Class, Student, User
from routes import admin_required

bp = Blueprint('base_data', __name__, url_prefix='/base_data')

# ---------- 院系 ----------
@bp.route('/department')
@login_required
@admin_required
def dept_list():
    departments = Department.query.all()
    return render_template('department/list.html', departments=departments)

@bp.route('/department/add', methods=['GET', 'POST'])
@login_required
@admin_required
def dept_add():
    if request.method == 'POST':
        try:
            dept = Department(
                dept_id=request.form['dept_id'],
                dept_name=request.form['dept_name'],
                dean=request.form.get('dean'),
                phone=request.form.get('phone'),
                office=request.form.get('office')
            )
            db.session.add(dept)
            db.session.commit()
            flash('院系添加成功', 'success')
            return redirect(url_for('base_data.dept_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{e}', 'danger')
    return render_template('department/form.html', dept=None)

@bp.route('/department/edit/<dept_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def dept_edit(dept_id):
    dept = Department.query.get_or_404(dept_id)
    if request.method == 'POST':
        try:
            dept.dept_name = request.form['dept_name']
            dept.dean = request.form.get('dean')
            dept.phone = request.form.get('phone')
            dept.office = request.form.get('office')
            db.session.commit()
            flash('院系更新成功', 'success')
            return redirect(url_for('base_data.dept_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{e}', 'danger')
    return render_template('department/form.html', dept=dept)

@bp.route('/department/delete/<dept_id>', methods=['POST'])
@login_required
@admin_required
def dept_delete(dept_id):
    dept = Department.query.get_or_404(dept_id)
    if Major.query.filter_by(dept_id=dept_id).first():
        flash('该院系下还有专业，无法删除', 'danger')
        return redirect(url_for('base_data.dept_list'))
    if User.query.filter_by(dept_id=dept_id).first():
        flash('该院系下还有教师，无法删除', 'danger')
        return redirect(url_for('base_data.dept_list'))
    db.session.delete(dept)
    db.session.commit()
    flash('院系已删除', 'info')
    return redirect(url_for('base_data.dept_list'))

# ---------- 专业 ----------
@bp.route('/major')
@login_required
@admin_required
def major_list():
    majors = Major.query.all()
    return render_template('major/list.html', majors=majors)

@bp.route('/major/add', methods=['GET', 'POST'])
@login_required
@admin_required
def major_add():
    if request.method == 'POST':
        try:
            major = Major(
                major_id=request.form['major_id'],
                major_name=request.form['major_name'],
                dept_id=request.form['dept_id'],
                duration=request.form.get('duration', type=int),
                degree_type=request.form.get('degree_type')
            )
            db.session.add(major)
            db.session.commit()
            flash('专业添加成功', 'success')
            return redirect(url_for('base_data.major_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{e}', 'danger')
    departments = Department.query.all()
    return render_template('major/form.html', departments=departments, major=None)

@bp.route('/major/edit/<major_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def major_edit(major_id):
    major = Major.query.get_or_404(major_id)
    if request.method == 'POST':
        try:
            major.major_name = request.form['major_name']
            major.dept_id = request.form['dept_id']
            major.duration = request.form.get('duration', type=int)
            major.degree_type = request.form.get('degree_type')
            db.session.commit()
            flash('专业更新成功', 'success')
            return redirect(url_for('base_data.major_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{e}', 'danger')
    departments = Department.query.all()
    return render_template('major/form.html', departments=departments, major=major)

@bp.route('/major/delete/<major_id>', methods=['POST'])
@login_required
@admin_required
def major_delete(major_id):
    major = Major.query.get_or_404(major_id)
    if Class.query.filter_by(major_id=major_id).first():
        flash('该专业下还有班级，无法删除', 'danger')
        return redirect(url_for('base_data.major_list'))
    db.session.delete(major)
    db.session.commit()
    flash('专业已删除', 'info')
    return redirect(url_for('base_data.major_list'))

# ---------- 班级 ----------
@bp.route('/class')
@login_required
@admin_required
def class_list():
    classes = Class.query.all()
    return render_template('class/list.html', classes=classes)

@bp.route('/class/add', methods=['GET', 'POST'])
@login_required
@admin_required
def class_add():
    if request.method == 'POST':
        try:
            cls = Class(
                class_id=request.form['class_id'],
                class_name=request.form['class_name'],
                major_id=request.form['major_id'],
                counselor_id=request.form.get('counselor_id'),   # 改为 counselor_id
                grade=request.form.get('grade', type=int)
            )
            db.session.add(cls)
            db.session.commit()
            flash('班级添加成功', 'success')
            return redirect(url_for('base_data.class_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{e}', 'danger')
    majors = Major.query.all()
    teachers = User.query.filter_by(role='teacher').all()   # 教师列表供选择
    return render_template('class/form.html', majors=majors, teachers=teachers, cls=None)

@bp.route('/class/edit/<class_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def class_edit(class_id):
    cls = Class.query.get_or_404(class_id)
    if request.method == 'POST':
        try:
            cls.class_name = request.form['class_name']
            cls.major_id = request.form['major_id']
            cls.counselor_id = request.form.get('counselor_id')   # 改为 counselor_id
            cls.grade = request.form.get('grade', type=int)
            db.session.commit()
            flash('班级更新成功', 'success')
            return redirect(url_for('base_data.class_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{e}', 'danger')
    majors = Major.query.all()
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('class/form.html', majors=majors, teachers=teachers, cls=cls)

@bp.route('/class/delete/<class_id>', methods=['POST'])
@login_required
@admin_required
def class_delete(class_id):
    cls = Class.query.get_or_404(class_id)
    if Student.query.filter_by(class_id=class_id).first():
        flash('该班级下还有学生，无法删除', 'danger')
        return redirect(url_for('base_data.class_list'))
    db.session.delete(cls)
    db.session.commit()
    flash('班级已删除', 'info')
    return redirect(url_for('base_data.class_list'))