from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_login import login_required
from services.file_service import save_file, allowed_file

bp = Blueprint('upload', __name__, url_prefix='/upload')

@bp.route('/file', methods=['POST'])
@login_required
def upload_file():
    file = request.files.get('file')
    if not file:
        return jsonify({'success': False, 'message': '无文件'}), 400
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': '不支持的文件类型'}), 400
    subfolder = request.form.get('type', 'photos')
    try:
        path = save_file(file, subfolder)
        return jsonify({'success': True, 'path': path})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/files/<path:subpath>')
def serve_uploaded(subpath):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], subpath)