from flask import (
    Blueprint, current_app, flash, redirect, render_template, request, url_for
)

from .models import Yarn, Fiber, Store, Link
from .forms import AddLinkForm, YarnForm, FilterForm
from . import db

bp = Blueprint('yarn', __name__, url_prefix='/yarn')

@bp.route('/browse', methods=['GET', 'POST'])
def browse():
    form = FilterForm()
    if request.method == 'POST':
        search_dict = {}
        search_dict['brand'] = Yarn.query.filter_by(brand=form.brand_name.data).all() if form.brand_name.data != '' else None
        search_dict['name'] = Yarn.query.filter_by(name=form.yarn_name.data).all() if form.yarn_name.data != '' else None
        search_dict['weight_name'] = Yarn.query.filter_by(weight_name=form.weight_name.data).all() if form.weight_name.data != '' else None
        if form.gauge_integer.data != '':
            if form.gauge_approx:
                search_dict['gauge'] = Yarn.query.filter_by(gauge=int(form.gauge_integer.data) - 1).all() + Yarn.query.filter_by(gauge=int(form.gauge_integer.data)).all() + Yarn.query.filter_by(gauge=int(form.gauge_integer.data) + 1).all()
            else:
                search_dict['gauge'] = Yarn.query.filter_by(gauge=form.gauge_integer.data).all()
        search_dict['texture'] = Yarn.query.filter_by(texture=form.texture.data).all() if form.texture.data != '' else None
        search_dict['color_style'] = Yarn.query.filter_by(color_style=form.color_style.data).all() if form.color_style.data != '' else None
        
        full_search = []
        for v in search_dict.values():
            if v is not None:
                full_search.append(v)
        yarn_list = list(set.intersection(*map(set,list(full_search))))
        yarn_list = [yarn.id for yarn in yarn_list]
        print(yarn_list)
        return redirect(url_for('yarn.results', yarn_list=yarn_list))
    return render_template('yarn_killer/yarn_browse.html', yarn_list=Yarn.query.all(), form=form)


@bp.route('/results/<yarn_list>')
def results(yarn_list):
    yarn_list = yarn_list.strip('[]').split(', ')
    yarn_list = [Yarn.query.get(x) for x in yarn_list]
    return render_template('yarn_killer/results.html', yarn_list=yarn_list)


@bp.route('/link_<id>/update')
def update_price(id):
    link = Link.query.get(id)
    link.update_price()
    return redirect(url_for('yarn.view_yarn', id=link.yarn_id))

@bp.route('/<id>')
def view_yarn(id):
    yarn = Yarn.query.get(id)
    sorted_links = []
    try:
        sorted_links = sorted(yarn.links, key=lambda link: link.current_price)
    except TypeError:
        for link in yarn.links:
            if link.current_price is None:
                link.update_price()
        sorted_links = sorted(yarn.links, key=lambda link: link.current_price)
    for link in yarn.links:
        if link.store_id is None:
            db.session.delete(link)
            db.session.commit()
    return render_template('yarn_killer/yarn_view.html', yarn=yarn, sorted_links=sorted_links, colorway_count=len(yarn.colorways))


@bp.route('/make_colorways/<id>', methods=['GET', 'POST'])
def make_colorways(id):
    for link in Yarn.query.get(id).links:
        link.extract_colorways()
    return redirect(url_for('yarn.view_yarn', id=link.yarn_id))


@bp.route('/<id>/edit', methods=('GET', 'POST'))
def edit_yarn(id):
    if id == 'new':
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
            texture=yarn.texture,
            color_style=yarn.color_style,
            discontinued=yarn.discontinued
        )
        for i in range(len(yarn.fibers)):
            form.fiber_type_list[i].fiber_type.data = yarn.fibers[i].type
            form.fiber_type_list[i].fiber_qty.data = yarn.fibers[i].amount
        if form.validate_on_submit():
            populate_yarn(yarn, form)
            populate_fibers(yarn, form)
            return redirect(url_for('yarn.view_yarn', id=yarn.id))
        return render_template('yarn_killer/yarn_edit.html', form=form)


@bp.route('/<id>/add_link', methods=('POST', 'GET'))
def add_link(id):
    def parse_name_from_url(link):
        if 'www.joann.com' in link:
            return 'Joann'
        elif 'www.yarnspirations.com' in link:
            return 'Yarnspirations'
        elif 'www.michaels.com' in link:
            return 'Michaels'
        elif 'www.lovecrafts.com' in link:
            return 'LoveCrafts'
        elif 'www.motherofpurlyarn.com' in link:
            return 'Mother of Purl'
        elif 'www.lionbrand.com' in link:
            return 'Lion Brand'
        elif 'www.yarn.com' in link:
            return 'WEBS'
        elif 'patternsbykraemer.com' in link:
            return 'Kraemer'
        else:
            flash('Invalid link passed to parse_name_from_url')
            return None


    yarn = Yarn.query.get(id)
    form = AddLinkForm()
    if form.validate_on_submit():
        link = Link.query.filter_by(url=form.url.data).first()
        if link is None:
            link = Link(url=form.url.data, yarn_id=yarn.id)
            db.session.add(link)
            db.session.commit()
            # I don't know if it's necessary to re-retrieve this to get the id or not
            link = Link.query.filter_by(url=form.url.data).first()
        store_name = parse_name_from_url(form.url.data)
        if store_name is not None:
            store_query = Store.query.filter_by(name=store_name).first()
            if store_query is None:
                store = Store(name=store_name)
                db.session.add(store)
                store.yarns.append(yarn)
                yarn.stores.append(store)
                db.session.commit()
                link.store_id = Store.query.filter_by(name=store.name).first().id
                db.session.commit()
            else:
                link.store_id = store_query.id
                if yarn not in store_query.yarns:
                    store_query.yarns.append(yarn)
                if store_query not in yarn.stores:
                    yarn.stores.append(store_query)
                db.session.commit()
            link.update_price()
            return redirect(url_for('yarn.view_yarn', id=yarn.id))
    return render_template('yarn_killer/add_link.html', yarn=yarn, form=form)



def populate_yarn(yarn, form):
    yarn.brand = form.brand_name.data
    yarn.name = form.yarn_name.data
    yarn.weight_name = form.weight_name.data
    yarn.gauge = form.gauge.data
    yarn.yardage = form.yardage.data
    yarn.weight_grams = form.weight_grams.data
    yarn.texture = form.texture.data
    yarn.color_style = form.color_style.data
    yarn.discontinued = form.discontinued.data
    db.session.add(yarn)
    db.session.commit()

def populate_fibers(yarn, form):
    fibers = {}
    for fiber in form.fiber_type_list.entries:
        if fiber.fiber_type.data != '' and fiber.fiber_type.data is not None:
            fibers[fiber.fiber_type.data] = fiber.fiber_qty.data
    if len(fibers) > 0:
        if sum(fibers.values()) > 100:
            if current_app.config.get('TESTING'):
                print('Fiber total > 100%')
            else:
                flash('Fiber total > 100%')
        else:
            for fiber_type, fiber_amount in fibers.items():
                yarn.add_fibers(fiber_type, fiber_amount)
    else:
        flash('The entered yarn has no fiber content.')