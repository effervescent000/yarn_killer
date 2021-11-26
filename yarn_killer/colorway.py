from flask import (
    Blueprint, current_app, flash, redirect, render_template, request, url_for
)

from .models import Colorway, Yarn
from . import db

bp = Blueprint('colorway', __name__, url_prefix='/colorway')

@bp.route('/manage')
def manage():
    return render_template('yarn_killer/colorways_manage.html', yarn_list=Yarn.query.all())


@bp.route('/update/<id>')
def update(id):
    def process_yarn(yarn):
        for link in yarn.links:
            link.extract_colorways(recheck=True)


    if id == 'all':
        yarn_list = [x for x in Yarn.query.all() if len(x.colorways) > 0]
        for yarn in yarn_list:
            process_yarn(yarn)
    else:
        process_yarn(Yarn.query.get(id))
    return redirect(url_for('colorway.manage'))