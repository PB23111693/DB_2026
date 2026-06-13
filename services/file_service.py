import os, uuid
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_file(file, subfolder='photos'):
    if not file or file.filename == '':
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    new_name = f"{uuid.uuid4().hex}.{ext}"
    new_name = secure_filename(new_name)
    target_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(target_dir, exist_ok=True)
    filepath = os.path.join(target_dir, new_name)
    file.save(filepath)
    # 如果是图片，生成缩略图（可选）
    if ext in ('jpg', 'jpeg', 'png', 'gif'):
        thumb_dir = os.path.join(target_dir, 'thumbnails')
        os.makedirs(thumb_dir, exist_ok=True)
        img = Image.open(filepath)
        img.thumbnail((200, 200))
        img.save(os.path.join(thumb_dir, f'thumb_{new_name}'))
    return f'{subfolder}/{new_name}'

def delete_file(relative_path):
    """删除服务器上的文件（包括缩略图），不会抛出异常"""
    if not relative_path:
        return
    # 构建完整路径：UPLOAD_FOLDER + 相对路径
    base = current_app.config['UPLOAD_FOLDER']
    full_path = os.path.join(base, relative_path)
    # 安全校验：确保路径在 UPLOAD_FOLDER 内，防止目录穿越
    if os.path.commonpath([os.path.abspath(full_path), os.path.abspath(base)]) != os.path.abspath(base):
        return
    try:
        if os.path.isfile(full_path):
            os.remove(full_path)
    except OSError:
        pass
    # 若为图片，尝试删除缩略图
    if relative_path.startswith('photos/') or relative_path.startswith('certificates/'):
        thumb_path = os.path.join(os.path.dirname(full_path), 'thumbnails', 'thumb_' + os.path.basename(full_path))
        try:
            if os.path.isfile(thumb_path):
                os.remove(thumb_path)
        except OSError:
            pass