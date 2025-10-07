# app/main/views.py
from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from . import main
from .. import db
from ..models import Post, User, Permission
from .forms import PostForm, EditProfileForm
from flask import abort
from app.models import User
from .forms import AdminResetPasswordForm




# ---------------- Index (عرض البوستات) ----------------
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

    # هل المستخدم يبي يشوف منشورات المتابعين فقط؟
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))

    # نحدد الاستعلام بناءً على الاختيار
    if show_followed and current_user.is_authenticated:
        query = current_user.followed_posts
    else:
        query = Post.query

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 10)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    posts = pagination.items

    return render_template('main/index.html',
                           form=form if can_write else None,
                           posts=posts,
                           pagination=pagination,
                           show_followed=show_followed)
# ---------------- إظهار كل المنشورات ----------------
@main.route('/all')
@login_required
def show_all():
    resp = redirect(url_for('main.index'))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)  # 30 يوم
    return resp

# ---------------- إظهار منشورات المتابعين فقط ----------------
@main.route('/followed')
@login_required
def show_followed():
    resp = redirect(url_for('main.index'))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)  # 30 يوم
    return resp

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

@main.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_administrator():
        abort(404)
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

# ---------------- حذف مستخدم ----------------
@main.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_administrator():
        abort(403)
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash("❌ You cannot delete yourself.")
        return redirect(url_for('main.admin_dashboard'))
    db.session.delete(user)
    db.session.commit()
    flash(f"✅ User '{user.username}' has been deleted.")
    return redirect(url_for('main.admin_dashboard'))


# ---------------- إعادة تعيين كلمة مرور المستخدم ----------------

@main.route('/admin/reset_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
def reset_password(user_id):
    if not current_user.is_administrator():
        abort(403)

    user = User.query.get_or_404(user_id)
    form = AdminResetPasswordForm()

    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        flash(f"🔑 Password for '{user.username}' has been updated successfully.")
        return redirect(url_for('main.admin_dashboard'))

    return render_template('admin_reset_password.html', form=form, user=user)

# ---------------- متابعة مستخدم ----------------
@main.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        flash("You cannot follow yourself!")
        return redirect(url_for('main.user_profile', username=username))
    if current_user.is_following(user):
        flash(f"You are already following {username}.")
        return redirect(url_for('main.user_profile', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f"You are now following {username}.")
    return redirect(url_for('main.user_profile', username=username))


# ---------------- إلغاء المتابعة ----------------
@main.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        flash("You cannot unfollow yourself!")
        return redirect(url_for('main.user_profile', username=username))
    if not current_user.is_following(user):
        flash(f"You are not following {username}.")
        return redirect(url_for('main.user_profile', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f"You unfollowed {username}.")
    return redirect(url_for('main.user_profile', username=username))


# ---------------- البحث عن المستخدم ----------------
@main.route('/search', methods=['GET', 'POST'])
@login_required
def search_user():
    from .forms import SearchUserForm
    form = SearchUserForm()
    user = None
    if form.validate_on_submit():
        username = form.username.data.strip()
        user = User.query.filter_by(username=username).first()
        if not user:
            flash("❌ User not found.")
            return redirect(url_for('main.search_user'))
        return redirect(url_for('main.user_profile', username=user.username))
    return render_template('main/search_user.html', form=form)
