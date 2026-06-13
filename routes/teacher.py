from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import text
from models import db, Course, Enrollment, Score, Student, User
from datetime import date

bp = Blueprint('teacher', __name__, url_prefix='/teacher')

@bp.route('/')
@login_required
def dashboard():
    """教师仪表盘：显示我的课程列表及每门课的学生人数"""
    if current_user.role != 'teacher':
        abort(403)
    courses = Course.query.filter_by(teacher_id=current_user.related_id).all()
    # 统计每门课的选课人数
    course_stats = []
    for c in courses:
        count = Enrollment.query.filter_by(course_id=c.course_id).count()
        course_stats.append({'course': c, 'student_count': count})
    return render_template('teacher/dashboard.html', courses=course_stats)

@bp.route('/course/<course_id>/students')
@login_required
def course_students(course_id):
    """查看某课程下的学生名单（含成绩）"""
    if current_user.role != 'teacher':
        abort(403)
    course = Course.query.get_or_404(course_id)
    # 验证该教师确实教授此课程
    if course.teacher_id != current_user.related_id:
        abort(403)

    # 查询选修该课程的所有学生及其成绩
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    student_scores = []
    for e in enrollments:
        student = Student.query.get(e.stu_id)
        score = Score.query.filter_by(enroll_id=e.enroll_id).first()
        student_scores.append({
            'student': student,
            'enrollment': e,
            'score': score
        })
    return render_template('teacher/course_students.html',
                           course=course, student_scores=student_scores)

@bp.route('/update_score/<int:enroll_id>', methods=['POST'])
@login_required
def update_score(enroll_id):
    if current_user.role != 'teacher':
        abort(403)
    enrollment = Enrollment.query.get_or_404(enroll_id)
    course = Course.query.get(enrollment.course_id)
    if not course or course.teacher_id != current_user.related_id:
        abort(403)

    try:
        score = Score.query.filter_by(enroll_id=enroll_id).first()
        if not score:
            score = Score(enroll_id=enroll_id)
            db.session.add(score)

        regular = request.form.get('regular')
        final = request.form.get('final')
        total = request.form.get('total')
        makeup = request.form.get('makeup')
        exam_method = request.form.get('exam_method')

        # 校验非负数
        for val_str, name in [(regular, '平时成绩'), (final, '期末成绩'), (total, '总评成绩'), (makeup, '补考成绩')]:
            if val_str and val_str.strip():
                try:
                    v = float(val_str)
                    if v < 0:
                        flash(f'{name}不能为负数', 'danger')
                        return redirect(url_for('teacher.course_students', course_id=course.course_id))
                except ValueError:
                    flash(f'{name}格式不正确', 'danger')
                    return redirect(url_for('teacher.course_students', course_id=course.course_id))

        # 只更新非空字段
        if regular and regular.strip():
            score.regular_score = float(regular)
        if final and final.strip():
            score.final_score = float(final)
        if total and total.strip():
            score.total_score = float(total)
        if makeup and makeup.strip():
            score.makeup_score = float(makeup)
        if exam_method:
            score.exam_method = exam_method

        db.session.commit()
        flash('成绩已更新', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'更新失败：{e}', 'danger')
    return redirect(url_for('teacher.course_students', course_id=course.course_id))