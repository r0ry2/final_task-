from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import User, Post
from . import admin
from ..models import admin_required
from .. import db


@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    users_count = User.query.count()
    posts_count = Post.query.count()
    return render_template('admin/dashboard.html',
                           users_count=users_count,
                           posts_count=posts_count)

@admin.route('/users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@admin.route('/posts')
@login_required
@admin_required
def manage_posts():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('admin/manage_posts.html', posts=posts)

