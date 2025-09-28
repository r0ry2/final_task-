import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class Config:
    SECRET_KEY = "secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///data.sqlite"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ADMIN = "admin@gmail.com"   # ايميل الأدمن
    
    # config.py

class Config:
    SECRET_KEY = "dev key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///socialblog.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ✅ عشان url_for يقدر يبني روابط كاملة في الإيميل
    SERVER_NAME = "127.0.0.1:5000"
    PREFERRED_URL_SCHEME = "http"

