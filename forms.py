from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, validators, TextAreaField

from models import User


def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise validators.ValidationError("User with that name already exists.")


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise validators.ValidationError("User with that email already exists.")


class RegisterForm(Form):
    username = StringField(
        'Username',
        validators=[
            validators.Length(min=4, max=25),
            name_exists
        ]
    )
    email = StringField(
        'Email',
        validators=[
            validators.Length(min=6, max=50),
            validators.Email(),
            email_exists
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            validators.DataRequired(),
            validators.EqualTo('confirm', message='Passwords do not match')
        ]
    )
    confirm = PasswordField('Confirm Password')


class LoginForm(Form):
    email = StringField(
        'Email',
        validators=[
            validators.DataRequired(),
            validators.Email()
        ]
    )
    password = PasswordField(
        'Password',
        validators=[validators.DataRequired()]
    )


class ArticleForm(Form):
    title = StringField(
        'Title',
        validators=[
            validators.DataRequired(),
        ]
    )
    body = TextAreaField(
        'Body',
        validators=[validators.Length(min=30)]
    )
