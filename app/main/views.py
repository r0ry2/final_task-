from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import main
from .. import db
from ..models import User
from .forms import EditProfileForm


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)  # يجيب البيانات الحالية
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash("Your profile has been updated.")
        return redirect(url_for('main.user_profile', username=current_user.username))
    return render_template('user/edit_profile.html', form=form)


@main.route('/')
def index():
    return render_template("main/index.html")


@main.route('/create')
@login_required
def create_post():
    return f"Hello {current_user.username}, write your post here!"


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/profile/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("user/profile.html", user=user)
