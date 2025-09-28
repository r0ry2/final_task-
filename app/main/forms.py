from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
    body = TextAreaField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditProfileForm(FlaskForm):
    name = StringField("Name", validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0, 64)])
    bio = TextAreaField("Bio", validators=[Length(0, 200)])
    submit = SubmitField("Save Changes")
