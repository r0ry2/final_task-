from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from ..models import User


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired()])
    confirm_new_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("new_password", message="Passwords must match")]
    )
    submit = SubmitField("Update Password")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")


class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[Length(0, 64)])
    email = StringField("Email", validators=[Length(0, 120)])
    name = StringField("Full Name", validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0, 64)])
    bio = TextAreaField("About me")
    submit = SubmitField("Save")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(),
                                                     EqualTo("password2", message="Passwords must match.")])
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already taken.")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered.")


class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField("New Password", validators=[DataRequired()])
    confirm_new_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("new_password", message="Passwords must match")]
    )
    submit = SubmitField("Reset Password")
