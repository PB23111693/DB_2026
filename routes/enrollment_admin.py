from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Enrollment, Student, Course, Score
from routes import admin_required
from datetime import date

bp = Blueprint('enrollment_admin', __name__, url_prefix='/enrollment_admin')

@bp.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def list_enrollments():
    if request.method == 'POST':
        stu_id = request.form['stu_id']
        course_id = request.form['course_id']
        semester = request.form.get('semester', '2024-2025-1')
        try:
            # 检查是否重复
            existing = Enrollment.query.filter_by(
                stu_id=stu_id, course_id=course_id, semester=semester
            ).first()
            if existing:
                flash('该选课记录已存在', 'warning')
            else:
                enrollment = Enrollment(
                    stu_id=stu_id,
                    course_id=course_id,
                    semester=semester,
                    enroll_date=date.today()
                )
                db.session.add(enrollment)
                db.session.commit()
                flash('选课添加成功', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{e}', 'danger')
        return redirect(url_for('enrollment_admin.list_enrollments'))

    enrollments = Enrollment.query.order_by(Enrollment.enroll_date.desc()).all()
    students = Student.query.all()
    courses = Course.query.all()
    return render_template('enrollment_admin/list.html',
                           enrollments=enrollments, students=students, courses=courses)

@bp.route('/delete/<int:enroll_id>', methods=['POST'])
@login_required
@admin_required
def delete_enrollment(enroll_id):
    enrollment = Enrollment.query.get_or_404(enroll_id)
    try:
        # 删除关联成绩
        Score.query.filter_by(enroll_id=enrollment.enroll_id).delete()
        db.session.delete(enrollment)
        db.session.commit()
        flash('选课记录已删除（含成绩）', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{e}', 'danger')
    return redirect(url_for('enrollment_admin.list_enrollments'))