from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)

from .models import Yarn
from . import db

bp = Blueprint('yarn', __name__, url_prefix='/yarn')

@bp.route('/browse')
def browse():
    pass


@bp.route('/<id>')
def view_yarn(id):
    pass
