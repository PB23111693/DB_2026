from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import db, Student, Class, Major, Enrollment, Score, Award, Punishment, MajorChange, StudentSummary, Course, User
from services.file_service import save_file, delete_file
from routes import admin_required
from werkzeug.security import generate_password_hash
from datetime import datetime

bp = Blueprint('student', __name__, url_prefix='/student')

@bp.route('/')
@login_required
def list():
    if current_user.role == 'student':
        student = Student.query.filter_by(stu_id=current_user.related_id).first()
        return render_template('student/list.html', students=[student] if student else [])
    students = Student.query.all()
    return render_template('student/list.html', students=students)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    if request.method == 'POST':
        try:
            stu_id = request.form['stu_id']
            # 检查该学号是否已被其他用户关联（学生角色）
            existing_user = User.query.filter_by(role='student', related_id=stu_id).first()
            if existing_user:
                flash(f'学号 {stu_id} 已绑定用户 {existing_user.username}，请先处理绑定关系', 'danger')
                classes = Class.query.all()
                return render_template('student/form.html', classes=classes, student=None)

            birth = request.form.get('birth')
            if birth:
                birth = datetime.strptime(birth, '%Y-%m-%d').date()
            student = Student(
                stu_id=stu_id,
                name=request.form['name'],
                gender=request.form.get('gender'),
                birth=birth,
                ethnicity=request.form.get('ethnicity'),
                political_status=request.form.get('political_status'),
                native_place=request.form.get('native_place'),
                id_card=request.form.get('id_card'),
                phone=request.form.get('phone'),
                email=request.form.get('email'),
                address=request.form.get('address'),
                enrollment_year=request.form.get('enrollment_year', type=int),
                status=request.form.get('status', '在读'),
                class_id=request.form['class_id']
            )
            photo = request.files.get('photo')
            if photo and photo.filename:
                student.photo_path = save_file(photo, 'photos')
            resume = request.files.get('resume')
            if resume and resume.filename:
                student.resume_path = save_file(resume, 'resumes')
            db.session.add(student)
            db.session.flush()

            # 同步创建学生用户（如果勾选）
            if request.form.get('create_user') == 'yes':
                if not User.query.filter_by(username=stu_id).first():
                    user = User(
                        username=stu_id,
                        password_hash=generate_password_hash(stu_id),
                        role='student',
                        name=student.name,
                        related_id=stu_id
                    )
                    db.session.add(user)
                    flash('已同步创建学生登录账号，用户名和初始密码均为学号。', 'info')
                else:
                    flash('该用户名已存在，跳过创建账号。', 'warning')

            db.session.commit()
            flash('学生添加成功', 'success')
            return redirect(url_for('student.list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'danger')
    classes = Class.query.all()
    return render_template('student/form.html', classes=classes, student=None)

@bp.route('/edit/<stu_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(stu_id):
    student = Student.query.get_or_404(stu_id)
    if request.method == 'POST':
        try:
            student.name = request.form['name']
            student.gender = request.form.get('gender')
            birth = request.form.get('birth')
            student.birth = datetime.strptime(birth, '%Y-%m-%d').date() if birth else None
            # ... 其他字段更新
            student.phone = request.form.get('phone')
            student.email = request.form.get('email')
            student.address = request.form.get('address')
            student.enrollment_year = request.form.get('enrollment_year', type=int)
            student.status = request.form.get('status', '在读')
            student.class_id = request.form['class_id']

            # 文件处理：如果上传了新文件，删除旧文件
            photo = request.files.get('photo')
            if photo and photo.filename:
                if student.photo_path:
                    delete_file(student.photo_path)  # 删除旧文件
                student.photo_path = save_file(photo, 'photos')
            resume = request.files.get('resume')
            if resume and resume.filename:
                if student.resume_path:
                    delete_file(student.resume_path)
                student.resume_path = save_file(resume, 'resumes')
            db.session.commit()
            flash('学生信息更新成功', 'success')
            return redirect(url_for('student.list'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'danger')
    classes = Class.query.all()
    return render_template('student/form.html', student=student, classes=classes)

@bp.route('/<stu_id>')
@login_required
def detail(stu_id):
    if current_user.role == 'student' and current_user.related_id != stu_id:
        abort(403)
    student = Student.query.get_or_404(stu_id)
    majors = Major.query.all()
    return render_template('student/detail.html', student=student, majors=majors)

@bp.route('/delete/<stu_id>', methods=['POST'])
@login_required
@admin_required
def delete(stu_id):
    student = Student.query.get_or_404(stu_id)
    try:
        # 1. 删除关联文件
        if student.photo_path:
            delete_file(student.photo_path)
        if student.resume_path:
            delete_file(student.resume_path)

        # 2. 清理关联的数据库记录
        enrollments = Enrollment.query.filter_by(stu_id=stu_id).all()
        for e in enrollments:
            Score.query.filter_by(enroll_id=e.enroll_id).delete()
        Enrollment.query.filter_by(stu_id=stu_id).delete()
        Award.query.filter_by(stu_id=stu_id).delete()
        Punishment.query.filter_by(stu_id=stu_id).delete()
        MajorChange.query.filter_by(stu_id=stu_id).delete()
        StudentSummary.query.filter_by(stu_id=stu_id).delete()

        # 3. 删除对应的用户账号（如果存在）
        user = User.query.filter_by(role='student', related_id=stu_id).first()
        if user:
            db.session.delete(user)

        # 4. 删除学生记录
        db.session.delete(student)
        db.session.commit()
        flash('学生及所有关联数据（包含用户账号）已删除，相关文件已清理', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'danger')
    return redirect(url_for('student.list'))

@bp.route('/my_courses')
@login_required
def my_courses():
    if current_user.role != 'student':
        abort(403)
    stu_id = current_user.related_id
    if not stu_id:
        flash('您的账号未关联学号，无法查看课程', 'warning')
        return redirect(url_for('index'))
    student = Student.query.get_or_404(stu_id)
    enrollments = Enrollment.query.filter_by(stu_id=stu_id).all()
    course_list = []
    for e in enrollments:
        course = Course.query.get(e.course_id)
        teacher = None
        if course and course.teacher_id:
            teacher = User.query.filter_by(role='teacher', related_id=course.teacher_id).first()
        score = Score.query.filter_by(enroll_id=e.enroll_id).first()
        course_list.append({
            'enrollment': e,
            'course': course,
            'teacher': teacher,
            'score': score
        })
    return render_template('student/my_courses.html', student=student, courses=course_list)

@bp.route('/enroll')
@login_required
def enroll_course():
    if current_user.role != 'student':
        abort(403)
    stu_id = current_user.related_id
    if not stu_id:
        flash('您的账号未关联学号，无法选课', 'warning')
        return redirect(url_for('index'))
    student = Student.query.get_or_404(stu_id)
    # 只显示已分配教师的课程
    all_courses = Course.query.filter(Course.teacher_id.isnot(None)).all()
    enrolled_course_ids = {
        e.course_id for e in Enrollment.query.filter_by(stu_id=stu_id).all()
    }
    return render_template('student/enroll.html',
                           student=student,
                           courses=all_courses,
                           enrolled_course_ids=enrolled_course_ids)

@bp.route('/enroll/<course_id>', methods=['POST'])
@login_required
def toggle_enroll(course_id):
    """选课/退选切换"""
    if current_user.role != 'student':
        abort(403)

    stu_id = current_user.related_id
    course = Course.query.get_or_404(course_id)
    semester = '2024-2025-1'  # 默认当前学期

    # 检查是否已选
    enrollment = Enrollment.query.filter_by(
        stu_id=stu_id, course_id=course_id, semester=semester
    ).first()

    try:
        if enrollment:
            # 退选（若已有成绩则阻止退选）
            if Score.query.filter_by(enroll_id=enrollment.enroll_id).first():
                flash('该课程已有成绩，无法退选', 'danger')
            else:
                db.session.delete(enrollment)
                db.session.commit()
                flash('退选成功', 'info')
        else:
            # 选课
            new_enroll = Enrollment(
                stu_id=stu_id,
                course_id=course_id,
                semester=semester,
                enroll_date=datetime.now().date()
            )
            db.session.add(new_enroll)
            db.session.commit()
            flash('选课成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'操作失败：{str(e)}', 'danger')

    return redirect(url_for('student.enroll_course'))