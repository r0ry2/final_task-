from faker import Faker
from app import create_app, db
from app.models import User, Post
import os
import sys

# إضافة جذر المشروع للمسار
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



app = create_app()
app.app_context().push()
fake = Faker()

# استخدم أي user موجود أو أنشئ واحداً
user = User.query.first()
if not user:
    print("No user found. Please create a user first.")
else:
    for i in range(100):
        p = Post(body=fake.paragraph(nb_sentences=5), author=user)
        Post.on_changed_body(p, p.body, None, None)  # لو لم تستخدم event listener
        db.session.add(p)
    db.session.commit()
    print("Added 100 fake posts.")
