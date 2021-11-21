from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)

from .models import Yarn, Fiber
from .forms import YarnForm
from . import db

bp = Blueprint('yarn', __name__, url_prefix='/yarn')

@bp.route('/browse')
def browse():
    yarn_list = Yarn.query.all()
    return render_template('yarn_killer/yarn_browse.html', yarn_list=yarn_list)


@bp.route('/<id>')
def view_yarn(id):
    yarn = Yarn.query.get(id)
    return render_template('yarn_killer/yarn_view.html', yarn=yarn)

@bp.route('/<id>/edit', methods=('GET', 'POST'))
def edit_yarn(id):
    if id == 'new':
        # create a new empty form
        form = YarnForm()
        if form.validate_on_submit():
            existing_yarn = Yarn.query.filter_by(brand=form.brand_name.data, name=form.yarn_name.data).first()
            if existing_yarn is None:
                yarn = Yarn()
                populate_yarn(yarn, form)
                # retrieve this yarn from the db
                yarn = Yarn.query.filter_by(brand=yarn.brand, name=yarn.name).first()
                populate_fibers(yarn, form)
                return redirect(url_for('yarn.view_yarn', id=yarn.id))
            else:
                flash('That yarn seems to already exist.')
        return render_template('yarn_killer/yarn_edit.html', form=form)
    else:
        yarn = Yarn.query.get(id)
        form = YarnForm(
            brand_name=yarn.brand, 
            yarn_name=yarn.name, 
            weight_name=yarn.weight_name, 
            gauge=yarn.gauge, 
            yardage=yarn.yardage,
            weight_grams=yarn.weight_grams,
            discontinued=yarn.discontinued
        )
        for i in range(len(yarn.fibers) - 1):
            form.fiber_type_list[i].fiber_type.data = yarn.fibers[i].type
            form.fiber_type_list[i].fiber_qty.data = yarn.fibers[i].amount
        if form.validate_on_submit():
            populate_yarn(yarn, form)
            populate_fibers(yarn, form)
            return redirect(url_for('yarn.view_yarn', id=yarn.id))
        return render_template('yarn_killer/yarn_edit.html', form=form)


def populate_yarn(yarn, form):
    yarn.brand = form.brand_name.data
    yarn.name = form.yarn_name.data
    yarn.weight_name = form.weight_name.data
    yarn.gauge = form.gauge.data
    yarn.yardage = form.yardage.data
    yarn.weight_grams = form.weight_grams.data
    yarn.discontinued = form.discontinued.data
    db.session.add(yarn)
    db.session.commit()

def populate_fibers(yarn, form):
    fibers = {}
    for fiber in form.fiber_type_list.entries:
        if fiber.fiber_type.data != '':
            fibers[fiber.fiber_type.data] = fiber.fiber_qty.data
    if len(fibers) > 0:
        for fiber_type, fiber_amount in fibers.items():
            fiber_new = Fiber(yarn_id=yarn.id, type=fiber_type, amount=fiber_amount)
            db.session.add(fiber_new)
            db.session.commit()
    else:
        flash('The entered yarn has no fiber content.')