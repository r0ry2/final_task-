from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required,current_user
from .. import db
from ..models import User
from . import auth
from .forms import LoginForm, RegistrationForm
from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from ..email import send_email   # ✅ جديد
from flask import request
from flask_login import current_user
from .forms import EditProfileForm
from .forms import ChangePasswordForm

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.verify_password(form.old_password.data):
            flash("Invalid current password.")
            return redirect(url_for('auth.change_password'))

        current_user.password = form.new_password.data
        db.session.commit()
        flash("Your password has been updated.")
        return redirect(url_for('main.index'))
    return render_template("auth/change_password.html", form=form)


@auth.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = EditProfileForm(obj=current_user)  # نمرر بيانات المستخدم الحالية
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your profile has been updated.")
        return redirect(url_for('auth.account'))
    return render_template("auth/account.html", form=form)

@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/resend')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template("auth/register.html", form=form)



@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember.data)
            return redirect(url_for('main.index'))
        flash("Invalid email or password.")
    return render_template("auth/login.html", form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('main.index'))

@auth.route('/register_simple', methods=['GET', 'POST'])   # ✅ غيرت الرابط
def register_simple():                                     # ✅ غيرت اسم الدالة
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.")
        return redirect(url_for('auth.login'))
    return render_template("auth/register.html", form=form)


@auth.route('/dashboard')
@login_required
def dashboard():
    return f"Welcome, {current_user.username}! This is your dashboard."

