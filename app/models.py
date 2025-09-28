from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app, abort
from . import db, login_manager
from functools import wraps
from datetime import datetime


# ---------------- Permissions ----------------
class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE = 0x04
    MODERATE = 0x08
    ADMIN = 0x80


# ---------------- Role Model ----------------
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Administrator': [0xff]
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = 0
            for perm in roles[r]:
                role.permissions |= perm
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return f"<Role {self.name}>"


# ---------------- User Model ----------------
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    # Profile info
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    bio = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=db.func.now())
    last_seen = db.Column(db.DateTime(), default=db.func.now())

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config.get('FLASK_ADMIN'):
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    # ---------------- Permissions ----------------
    def can(self, perm):
        return self.role is not None and (self.role.permissions & perm) == perm

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    # ---------------- Password ----------------
    @property
    def password(self):
        raise AttributeError("password is not readable")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # ---------------- Account Confirmation ----------------
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'confirm': self.id})

    def confirm(self, token, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expiration)
        except Exception:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    # ---------------- Activity ----------------
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<User {self.username}>"


# ---------------- Helpers ----------------
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMIN)(f)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
