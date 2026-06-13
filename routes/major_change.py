from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import text
from models import db, MajorChange
from routes import teacher_or_admin_required
from datetime import date

bp = Blueprint('major_change', __name__, url_prefix='/major_change')

@bp.route('/')
@login_required
def list():
    changes = MajorChange.query.order_by(MajorChange.change_date.desc()).all()
    return render_template('major_change/list.html', changes=changes)

@bp.route('/new', methods=['POST'])
@login_required
@teacher_or_admin_required
def new_change():
    try:
        stu_id = request.form['stu_id']
        new_major_id = request.form['new_major']
        change_date = request.form.get('change_date', date.today())
        approval_doc = request.form.get('approval_doc', '')
        reason = request.form.get('reason', '')
        operator = current_user.username

        # 使用 text() 包装原生 SQL
        with db.engine.begin() as conn:
            conn.execute(
                text("CALL sp_change_major(:stu, :new, :date, :doc, :reason, :op)"),
                {'stu': stu_id, 'new': new_major_id, 'date': change_date,
                 'doc': approval_doc, 'reason': reason, 'op': operator}
            )
        flash('专业变更成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'变更失败：{e}', 'danger')
    return redirect(url_for('student.detail', stu_id=request.form.get('stu_id'))
                    if request.form.get('stu_id') else url_for('major_change.list'))

@bp.route('/delete/<int:change_id>', methods=['POST'])
@login_required
@teacher_or_admin_required
def delete_change(change_id):
    change = MajorChange.query.get_or_404(change_id)
    stu_id = change.stu_id
    try:
        db.session.delete(change)
        db.session.commit()
        flash('专业变更记录已删除', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{e}', 'danger')
    if stu_id:
        return redirect(url_for('student.detail', stu_id=stu_id))
    return redirect(url_for('major_change.list'))