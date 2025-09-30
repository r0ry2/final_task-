import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "dev key"

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        "sqlite:///" + os.path.join(basedir, "socialblog.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FLASK_ADMIN = "admin@gmail.com"   # ايميل الأدمن

    # Pagination
    POSTS_PER_PAGE = 10

    # إعدادات لتوليد روابط كاملة في الإيميلات (مثلاً reset password, confirm email)
    SERVER_NAME = "127.0.0.1:5000"
    PREFERRED_URL_SCHEME = "http"


