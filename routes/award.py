from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Award, Punishment, StudentSummary
from services.file_service import save_file
from routes import teacher_or_admin_required
from datetime import date

bp = Blueprint('award', __name__, url_prefix='/award')

@bp.route('/add_award', methods=['POST'])
@login_required
@teacher_or_admin_required
def add_award():
    try:
        award = Award(
            stu_id=request.form['stu_id'],
            award_name=request.form['award_name'],
            award_level=request.form.get('award_level'),
            award_date=request.form.get('award_date', date.today()),
            issuer=request.form.get('issuer')
        )
        file = request.files.get('certificate')
        if file and file.filename:
            award.certificate_path = save_file(file, 'certificates')
        db.session.add(award)
        db.session.commit()
        flash('奖励添加成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'添加失败：{e}', 'danger')
    return redirect(url_for('student.detail', stu_id=request.form['stu_id']))

@bp.route('/delete_award/<int:award_id>', methods=['POST'])
@login_required
@teacher_or_admin_required
def delete_award(award_id):
    award = Award.query.get_or_404(award_id)
    stu_id = award.stu_id
    try:
        db.session.delete(award)
        db.session.commit()
        flash('奖励已删除', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{e}', 'danger')
    return redirect(url_for('student.detail', stu_id=stu_id))

@bp.route('/add_punish', methods=['POST'])
@login_required
@teacher_or_admin_required
def add_punish():
    try:
        lift_date = request.form.get('lift_date')
        if lift_date:
            lift_date = date.fromisoformat(lift_date)
        punishment = Punishment(
            stu_id=request.form['stu_id'],
            punish_type=request.form['punish_type'],
            punish_date=request.form['punish_date'],
            reason=request.form.get('reason'),
            lift_date=lift_date
        )
        file = request.files.get('file')
        if file and file.filename:
            punishment.file_path = save_file(file, 'documents')
        db.session.add(punishment)
        db.session.commit()
        flash('处罚添加成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'添加失败：{e}', 'danger')
    return redirect(url_for('student.detail', stu_id=request.form['stu_id']))

@bp.route('/delete_punish/<int:punish_id>', methods=['POST'])
@login_required
@teacher_or_admin_required
def delete_punish(punish_id):
    punishment = Punishment.query.get_or_404(punish_id)
    stu_id = punishment.stu_id
    try:
        db.session.delete(punishment)
        db.session.commit()
        # 检查是否还有未解除的处分，更新 has_punish
        remaining = Punishment.query.filter(
            Punishment.stu_id == stu_id,
            (Punishment.lift_date == None) | (Punishment.lift_date > date.today())
        ).first()
        summary = StudentSummary.query.get(stu_id)
        if summary:
            summary.has_punish = bool(remaining)
            db.session.commit()
        flash('处罚已删除', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{e}', 'danger')
    return redirect(url_for('student.detail', stu_id=stu_id))