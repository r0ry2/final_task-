from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail   # ✅ جديد

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
migrate = Migrate()
mail = Mail()   # ✅ جديد




def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # إعدادات البريد (من الفصل 12)
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = '<your-email>@gmail.com'   # غيّرها
    app.config['MAIL_PASSWORD'] = '<your-password>'          # غيّرها
    app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)   # ✅ جديد

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
