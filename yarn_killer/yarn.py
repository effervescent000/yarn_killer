from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)

from .models import Yarn, Fiber
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
            existing_yarn = Yarn.query.filter_by(brand=form.brand_name.data, name=form.yarn_name.data).first()
            if existing_yarn is None:
                yarn = Yarn(
                    brand=form.brand_name.data,
                    name=form.yarn_name.data,
                    weight_name=form.weight_name.data,
                    gauge=form.gauge.data,
                    yardage=form.yardage.data,
                    weight_grams=form.weight_grams.data,
                    discontinued=form.discontinued.data,
                )
                db.session.add(yarn)
                db.session.commit()
                # retrieve this yarn from the db
                yarn = Yarn.query.filter_by(brand=yarn.brand, name=yarn.name).first()
                fibers = {}
                for fiber in form.fiber_type_list.entries:
                    if fiber.type != '':
                        fibers[fiber.type] = fiber.amount.data
                if len(fibers) > 0:
                    for fiber_type, fiber_amount in fibers.items():
                        fiber_new = Fiber(yarn_id=yarn.id, type=fiber_type, amount=fiber_amount)
                        db.session.add(fiber_new)
                        db.session.commit()
                else:
                    flash('The entered yarn has no fiber content.')
                return redirect(url_for('yarn.view_yarn', id=yarn.id))
            else:
                flash('That yarn seems to already exist.')
        return render_template('yarn_killer/yarn_edit.html', form=form)
    else:
        # create a form populated with the yarn's data
        pass
