from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)

from .models import Yarn
from .forms import YarnForm
from . import db

bp = Blueprint('yarn', __name__, url_prefix='/yarn')

@bp.route('/browse')
def browse():
    pass


@bp.route('/<id>')
def view_yarn(id):
    pass

@bp.route('/<id>/edit', methods=('GET', 'POST'))
def edit_yarn(id):
    if id == 'new':
        # create a new empty form
        form = YarnForm()
        if form.validate_on_submit():
            pass
        return render_template('yarn_killer/edit_yarn.html', form=form)
    else:
        # create a form populated with the yarn's data
        pass
