from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from flask_login import login_required, logout_user, current_user, login_user

from .models import User
from .forms import SignUpForm, LoginForm
from . import db, login_manager

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup', methods=('GET', 'POST'))
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user is None:
            user = User()
            user.username = form.username.data
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index.index'))
        else:
            flash('A user with that name already exists')
    return render_template('yarn_killer/signup.html', form=form)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        # redirect to homepage
        pass
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(password=form.password.data):
            login_user(user)
            # TODO look into how to secure the next_page thing
            next_page = request.args.get('next')
            # return redirect to homepage or next_page
        flash('Invalid username/password combination')


@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view that page')
    return redirect(url_for('auth.login'))