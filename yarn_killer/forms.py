from flask import Flask
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField
from wtforms.fields.simple import PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, Email, EqualTo

# user/login-related forms
class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[
        Length(min=6, message='Choose a longer password'),
        InputRequired()
    ])
    confirm_password = PasswordField('Password', validators=[
        InputRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')