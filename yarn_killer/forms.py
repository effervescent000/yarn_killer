from flask import Flask
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField
from wtforms import PasswordField, SubmitField, SelectField, IntegerField, BooleanField, FormField, FieldList
from wtforms.validators import InputRequired, Length, Email, EqualTo, Optional

from .utils import get_yarn_weight_tuple, get_fiber_types_list


class FiberForm(FlaskForm):
    fiber_type = SelectField('Fiber', choices=get_fiber_types_list(), validators=[Optional()])
    fiber_qty = IntegerField('%', validators=[Optional()])


class YarnForm(FlaskForm):
    brand_name = StringField('Brand', validators=[InputRequired()])
    yarn_name = StringField('Yarn', validators=[InputRequired()])
    weight_name = SelectField('Weight', choices=get_yarn_weight_tuple())
    gauge = IntegerField('Gauge', validators=[InputRequired()])
    yardage = IntegerField('Yardage', validators=[InputRequired()])
    weight_grams = IntegerField('Weight in grams', validators=[InputRequired()])
    discontinued = BooleanField('Discontinued?')
    fiber_type_list = FieldList(FormField(FiberForm), min_entries=5)

    submit = SubmitField('Submit')

# user/login-related forms
class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[
        Length(min=6, message='Choose a longer password'),
        InputRequired()
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        InputRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')