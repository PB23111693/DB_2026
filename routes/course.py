from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Course, Department, User, Enrollment, Score
from services.file_service import save_file, delete_file
from routes import admin_required

bp = Blueprint('course', __name__, url_prefix='/course')

@bp.route('/')
@login_required
def list():
    teacher_id = request.args.get('teacher_id')
    if teacher_id:
        courses = Course.query.filter_by(teacher_id=teacher_id).all()
    else:
        courses = Course.query.all()
    return render_template('course/list.html', courses=courses)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    if request.method == 'POST':
        try:
            course = Course(
                course_id=request.form['course_id'],
                course_name=request.form['course_name'],
                credit=request.form.get('credit', type=float),
                hours=request.form.get('hours', type=int),
                dept_id=request.form['dept_id'],
                course_type=request.form.get('course_type'),
                teacher_id=request.form.get('teacher_id') or None
            )
            syllabus = request.files.get('syllabus')
            if syllabus and syllabus.filename:
                course.syllabus_path = save_file(syllabus, 'syllabi')
            db.session.add(course)
            db.session.commit()
            flash('课程添加成功', 'success')
            return redirect(url_for('course.list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'danger')
    departments = Department.query.all()
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('course/form.html', departments=departments, teachers=teachers, course=None)

@bp.route('/edit/<course_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(course_id):
    course = Course.query.get_or_404(course_id)
    if request.method == 'POST':
        try:
            course.course_name = request.form['course_name']
            course.credit = request.form.get('credit', type=float)
            course.hours = request.form.get('hours', type=int)
            course.dept_id = request.form['dept_id']
            course.course_type = request.form.get('course_type')
            course.teacher_id = request.form.get('teacher_id') or None
            syllabus = request.files.get('syllabus')
            if syllabus and syllabus.filename:
                if course.syllabus_path:
                    delete_file(course.syllabus_path)
                course.syllabus_path = save_file(syllabus, 'syllabi')
            db.session.commit()
            flash('课程更新成功', 'success')
            return redirect(url_for('course.list'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'danger')
    departments = Department.query.all()
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('course/form.html', departments=departments, teachers=teachers, course=course)

@bp.route('/delete/<course_id>', methods=['POST'])
@login_required
@admin_required
def delete(course_id):
    course = Course.query.get_or_404(course_id)
    try:
        # 删除大纲文件
        if course.syllabus_path:
            delete_file(course.syllabus_path)
        # 删除该课程相关的选课和成绩（如果有）
        enrollments = Enrollment.query.filter_by(course_id=course_id).all()
        for e in enrollments:
            Score.query.filter_by(enroll_id=e.enroll_id).delete()
        Enrollment.query.filter_by(course_id=course_id).delete()
        db.session.delete(course)
        db.session.commit()
        flash('课程已删除，相关文件及选课成绩已清理', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'danger')
    return redirect(url_for('course.list'))