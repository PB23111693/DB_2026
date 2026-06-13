import os
from flask import Flask, render_template, url_for
from flask_login import LoginManager, login_required, current_user
from config import Config
from models import db, User
from werkzeug.security import generate_password_hash

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    for sub in ['photos', 'resumes', 'certificates', 'syllabi', 'documents']:
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], sub), exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    with app.app_context():
        db.create_all()
        # 创建默认管理员
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('123456'),
                role='admin',
                name='系统管理员',
                related_id=None
            )
            db.session.add(admin)
            db.session.commit()
            print('已创建默认管理员账户: admin / 123456')
        # 修复 SQL 脚本中 placeholder 密码的用户
        placeholder = 'scrypt:placeholder_will_be_updated_by_app'
        broken_users = User.query.filter(User.password_hash.like('%placeholder%')).all()
        for u in broken_users:
            u.password_hash = generate_password_hash('123456')
            print(f'已修复用户 {u.username} 的密码为 123456')
        if broken_users:
            db.session.commit()

    from routes import student, course, score, major_change, award, upload, auth, user, base_data, teacher, enrollment_admin
    app.register_blueprint(student.bp)
    app.register_blueprint(course.bp)
    app.register_blueprint(score.bp)
    app.register_blueprint(major_change.bp)
    app.register_blueprint(award.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(base_data.bp)
    app.register_blueprint(teacher.bp)
    app.register_blueprint(enrollment_admin.bp)

    from models import User as UserModel
    app.jinja_env.globals['get_teacher_by_related_id'] = lambda rid: UserModel.query.filter_by(role='teacher', related_id=rid).first()

    @app.route('/')
    @login_required
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app_instance = create_app()
    app_instance.run(debug=True, port=5000)