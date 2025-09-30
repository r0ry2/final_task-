# app/auth/views.py
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from . import auth
from .. import db
from ..models import User, admin_required
from .forms import (
    LoginForm, RegistrationForm, EditProfileForm,
    ChangePasswordForm, ResetPasswordRequestForm, ResetPasswordForm
)
from ..email import send_email
from itsdangerous import URLSafeTimedSerializer as Serializer


@auth.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_confirmation_token()
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            print("🔗 Password reset link:", reset_url)
            flash("Check your email for a password reset link.")
        else:
            flash("Email not found.")
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', form=form)


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            s = Serializer(current_app.config['SECRET_KEY'])
            data = s.loads(token, max_age=3600)
            user = User.query.get(data.get('confirm'))
        except:
            flash("The reset link is invalid or has expired.")
            return redirect(url_for('auth.reset_password_request'))

        if user:
            user.password = form.new_password.data
            db.session.commit()
            flash("✅ Your password has been reset. Please log in.")
            return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.verify_password(form.old_password.data):
            flash(' Wrong current password.')
            return redirect(url_for('auth.change_password'))
        current_user.password = form.new_password.data
        db.session.commit()
        flash('Your password has been updated.')
        return redirect(url_for('main.user_profile', username=current_user.username))
    return render_template('auth/change_password.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember.data)

            #  إذا المستخدم أدمن → لوحة التحكم
            if user.is_administrator():
                return redirect(url_for('admin.dashboard'))

            #  إذا مستخدم عادي → الصفحة الرئيسية
            return redirect(url_for('main.index'))

        flash("Invalid email or password.")
    return render_template("auth/login.html", form=form)


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
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
                    email=form.email.data)
        user.password = form.password.data   # ✅ نستخدم setter هنا
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template("auth/register.html", form=form)


@auth.route('/confirm/<token>')
def confirm(token):
    if current_user.is_authenticated and current_user.confirmed:
        return redirect(url_for('main.index'))
    user = None
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token, max_age=3600)
        user = User.query.get(data.get('confirm'))
    except (BadSignature, SignatureExpired):
        flash('The confirmation link is invalid or has expired.')
        return redirect(url_for('main.index'))
    if user and user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('Confirmation failed. Please try again.')
    return redirect(url_for('main.index'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('main.index'))


@auth.route('/dashboard')
@login_required
def dashboard():
    return f"Welcome, {current_user.username}! This is your dashboard."


@auth.route('/admin-only')
@login_required
@admin_required
def admin_only():
    return "This page is for administrators only!"
