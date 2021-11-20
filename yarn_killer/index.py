from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)

from . import db

bp = Blueprint('index', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    return render_template('yarn_killer/index.html')
