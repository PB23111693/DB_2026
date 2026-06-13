from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, abort
from flask_login import login_required, current_user
from models import db, Student, Course, Enrollment, Score, StudentSummary
from services.pdf_service import generate_transcript
from routes import teacher_or_admin_required
from datetime import date

bp = Blueprint('score', __name__, url_prefix='/score')

@bp.route('/manage', methods=['GET', 'POST'])
@login_required
@teacher_or_admin_required
def manage():
    if current_user.role == 'teacher':
        courses = Course.query.filter_by(teacher_id=current_user.related_id).all()
    else:
        courses = Course.query.all()

    if request.method == 'POST':
        try:
            stu_id = request.form['stu_id']
            course_id = request.form['course_id']
            semester = request.form.get('semester', '2024-2025-1')

            enroll = Enrollment.query.filter_by(
                stu_id=stu_id, course_id=course_id, semester=semester
            ).first()
            if not enroll:
                flash('该学生尚未选修此课程，请先添加选课记录！', 'warning')
                return redirect(url_for('score.manage'))

            if current_user.role == 'teacher':
                course = Course.query.get(course_id)
                if not course or course.teacher_id != current_user.related_id:
                    abort(403)

            score = Score.query.filter_by(enroll_id=enroll.enroll_id).first()
            if not score:
                score = Score(enroll_id=enroll.enroll_id)
                db.session.add(score)

            # 获取表单数据，只更新非空字段
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
                            return redirect(url_for('score.manage'))
                    except ValueError:
                        flash(f'{name}格式不正确', 'danger')
                        return redirect(url_for('score.manage'))

            # 只更新用户实际填写的字段
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
            flash('成绩保存成功', 'success')
            return redirect(url_for('score.manage'))
        except Exception as e:
            db.session.rollback()
            flash(f'成绩保存失败：{str(e)}', 'danger')

    students = Student.query.all()
    if current_user.role == 'teacher':
        scores = Score.query.join(Enrollment).join(Course).filter(
            Course.teacher_id == current_user.related_id
        ).all()
    else:
        scores = Score.query.options(
            db.joinedload(Score.enrollment).joinedload(Enrollment.student),
            db.joinedload(Score.enrollment).joinedload(Enrollment.course)
        ).all()
    return render_template('score/manage.html',
                           students=students, courses=courses, scores=scores)

@bp.route('/delete/<int:score_id>', methods=['POST'])
@login_required
@teacher_or_admin_required
def delete_score(score_id):
    score = Score.query.get_or_404(score_id)
    if current_user.role == 'teacher':
        course = score.enrollment.course if score.enrollment else None
        if not course or course.teacher_id != current_user.related_id:
            abort(403)
    try:
        enroll_id = score.enroll_id
        stu_id = score.enrollment.stu_id if score.enrollment else None
        db.session.delete(score)
        enrollment = Enrollment.query.get(enroll_id)
        if enrollment:
            db.session.delete(enrollment)
        db.session.commit()
        if stu_id:
            with db.engine.begin() as conn:
                conn.execute(
                    "UPDATE student_summary SET gpa = fn_calc_student_gpa(:sid), total_credits = (SELECT COALESCE(SUM(c.credit),0) FROM score s JOIN enrollment e ON s.enroll_id = e.enroll_id JOIN course c ON e.course_id = c.course_id WHERE e.stu_id = :sid AND s.total_score >= 60) WHERE stu_id = :sid",
                    {'sid': stu_id}
                )
        flash('成绩已删除', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'danger')
    return redirect(url_for('score.manage'))

@bp.route('/transcript/<stu_id>')
@login_required
def download_transcript(stu_id):
    if current_user.role == 'student' and current_user.related_id != stu_id:
        abort(403)
    student = Student.query.get_or_404(stu_id)
    enrollments = Enrollment.query.filter_by(stu_id=stu_id).all()
    score_data = []
    for e in enrollments:
        if e.score and e.course:
            score_data.append({
                'course_name': e.course.course_name,
                'credit': float(e.course.credit) if e.course.credit else 0,
                'regular': float(e.score.regular_score) if e.score.regular_score else 0,
                'final': float(e.score.final_score) if e.score.final_score else 0,
                'total': float(e.score.total_score) if e.score.total_score else 0,
                'total_score': float(e.score.total_score) if e.score.total_score else 0
            })
    pdf_buffer = generate_transcript(student, score_data)
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=transcript_{stu_id}.pdf'
    return response

@bp.route('/stats')
@login_required
@teacher_or_admin_required
def stats():
    from sqlalchemy import func
    stats_query = db.session.query(
        Course.course_name,
        func.avg(Score.total_score).label('avg_score'),
        func.max(Score.total_score).label('max_score'),
        func.min(Score.total_score).label('min_score')
    ).join(Enrollment, Score.enroll_id == Enrollment.enroll_id)\
     .join(Course, Enrollment.course_id == Course.course_id)\
     .group_by(Course.course_id).all()

    rank_query = db.session.query(
        Student.name,
        func.sum(Score.total_score * Course.credit).label('weighted_sum'),
        func.sum(Course.credit).label('total_credits')
    ).select_from(Score)\
     .join(Enrollment, Score.enroll_id == Enrollment.enroll_id)\
     .join(Course, Enrollment.course_id == Course.course_id)\
     .join(Student, Enrollment.stu_id == Student.stu_id)\
     .group_by(Student.stu_id)\
     .order_by(func.sum(Score.total_score * Course.credit) / func.sum(Course.credit)).all()

    rankings = []
    for r in rank_query:
        if r.total_credits and float(r.total_credits) > 0:
            gpa = float(r.weighted_sum) / float(r.total_credits)
        else:
            gpa = 0
        rankings.append({'name': r.name, 'gpa': round(gpa, 2)})
    rankings = sorted(rankings, key=lambda x: x['gpa'], reverse=True)
    for idx, item in enumerate(rankings, 1):
        item['rank'] = idx

    return render_template('score/stats.html', stats=stats_query, rankings=rankings)