from flask import render_template
from flask_login import login_required, current_user
from . import main

@main.route('/')
def index():
    return render_template("main/index.html")

@main.route('/create')
@login_required
def create_post():
    return f"Hello {current_user.username}, write your post here!"

