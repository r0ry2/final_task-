# app/main/views.py
from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from . import main
from .. import db
from ..models import Post, User, Permission
from .forms import PostForm, EditProfileForm


# ---------------- Index (عرض البوستات) ----------------
@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    # عرض فورم النشر فقط للمستخدمين المصرّح لهم بالكتابة
    can_write = current_user.is_authenticated and current_user.can(Permission.WRITE)
    if can_write and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        flash('Your post has been published.')
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 10)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    posts = pagination.items

    return render_template('main/index.html',
                           form=form if can_write else None,
                           posts=posts,
                           pagination=pagination)


# ---------------- عرض بوست واحد ----------------
@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('main/post.html', post=post)


# ---------------- تعديل بوست ----------------
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    # السماح بتعديل المؤلف أو الأدمن فقط
    if current_user != post.author and not current_user.is_administrator():
        abort(403)

    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('main.post', id=post.id))
    return render_template('main/edit_post.html', form=form)


# ---------------- إنشاء بوست (صفحة مستقلة) ----------------
@main.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        flash("✅ Your post has been created.")
        return redirect(url_for('main.index'))
    return render_template("main/create_post.html", form=form)


# ---------------- تعديل البروفايل ----------------
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash("Your profile has been updated.")
        return redirect(url_for('main.user_profile', username=current_user.username))
    return render_template('user/edit_profile.html', form=form)


# ---------------- عرض بروفايل مستخدم ----------------
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/profile/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("user/profile.html", user=user)
