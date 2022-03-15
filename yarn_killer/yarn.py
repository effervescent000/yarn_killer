from xmlrpc.client import boolean
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
)

from .models import Yarn, Fiber, Image, Store, Link
from .schema import YarnSchema
from . import db

bp = Blueprint("yarn", __name__, url_prefix="/yarn")
one_yarn_schema = YarnSchema()
multi_yarn_schema = YarnSchema(many=True)


# GET endpoints


@bp.route("/get/<id>", methods=["GET"])
def get_yarn_by_id(id):
    return jsonify(one_yarn_schema.dump(Yarn.query.get(id)))


@bp.route("/get_all", methods=["GET"])
def get_yarn_list():
    all_yarn = Yarn.query.all()
    return jsonify(multi_yarn_schema.dump(all_yarn))


@bp.route("/get", methods=["GET"])
def get_yarn_results():
    if len(request.args) > 0:

        brand = request.args.get("brand")
        name = request.args.get("name")
        gauge = request.args.get("gauge", type=int)
        approx = request.args.get("approx", default=False, type=boolean)
        weight_name = request.args.get("weightName")
        texture = request.args.get("texture")
        color_style = request.args.get("colorStyle")

        all_results = []
        if brand != None:
            all_results.append(Yarn.query.filter_by(brand=brand).all())
        if name != None:
            all_results.append(Yarn.query.filter(Yarn.name.contains(name)).all())
        if gauge != None:
            if approx:
                all_results.append(
                    Yarn.query.filter(
                        Yarn.gauge > gauge - 2, Yarn.gauge < gauge + 2
                    ).all()
                )
            else:
                all_results.append(Yarn.query.filter_by(gauge=gauge).all())
        if weight_name != None:
            all_results.append(Yarn.query.filter_by(weight_name=weight_name).all())
        if texture != None:
            all_results.append(Yarn.query.filter_by(texture=texture).all())
        if color_style != None:
            all_results.append(Yarn.query.filter_by(color_style=color_style).all())

        return jsonify(
            multi_yarn_schema.dump(list(set.intersection(*map(set, all_results))))
        )
    return jsonify(multi_yarn_schema.dump(Yarn.query.all()))


@bp.route("/brands", methods=["GET"])
def get_brands():
    brands = []
    yarn_list = Yarn.query.all()
    for yarn in yarn_list:
        if yarn.brand not in brands:
            brands.append(yarn.brand)
    return jsonify(brands)


# POST endpoints


@bp.route("/add", methods=["POST"])
def add_yarn():
    data = request.get_json()

    brand = data.get("brand")
    name = data.get("name")
    weight_name = data.get("weightName")
    gauge = data.get("gauge")
    yardage = data.get("yardage")
    weight_grams = data.get("unitWeight")
    texture = data.get("texture")
    color_style = data.get("colorStyle")
    discontinued = data.get("discontinued")

    if brand == "":
        return jsonify("Must include a brand name")
    if name == "":
        return jsonify("Must include a yarn name")

    yarn = Yarn.query.filter_by(brand=brand, name=name).first()
    if yarn == None:
        if weight_name == "":
            return jsonify("Must include a weight band")
        if gauge == "":
            return jsonify("Must include a gauge")

        yarn = Yarn(
            brand=brand,
            name=name,
            weight_name=weight_name,
            gauge=gauge,
            yardage=yardage,
            weight_grams=weight_grams,
            texture=texture,
            color_style=color_style,
            discontinued=discontinued,
        )
        db.session.add(yarn)
        db.session.commit()

        fiber_dict = {}
        for i in range(1, 5):
            fiber_data = data.get(f"selectFiber{i}")
            if fiber_data != "":
                fiber_dict[fiber_data] = int(data.get(f"numberFiber{i}"))
        for fiber, amount in fiber_dict.items():
            new_fiber = Fiber(yarn_id=yarn.id, type=fiber, amount=amount)
            db.session.add(new_fiber)
            db.session.commit()

    return jsonify(one_yarn_schema.dump(yarn))


@bp.route("/image", methods=["POST"])
def add_image_to_yarn():
    data = request.get_json()
    yarn_id = data.get("yarn_id")
    if yarn_id == None:
        return jsonify("Error: No ID included in request")

    url = data.get("url")
    if url == None:
        return jsonify("Error: No URL included in request")

    label = data.get("label")
    colorway_id = data.get("colorway_id") if data.get("colorway_id") != None else 0
    new_image = Image(yarn_id=yarn_id, colorway_id=colorway_id, url=url, label=label)
    db.session.add(new_image)
    db.session.commit()


# PUT endpoints


@bp.route("/update", methods=["PUT"])
def update_yarn_by_id():
    data = request.get_json()

    id = data.get("id")

    if id == None:
        return jsonify("Error: No ID included in request")

    brand = data.get("brand")
    name = data.get("name")
    weight_name = data.get("weight_name")
    gauge = data.get("gauge")
    yardage = data.get("yardage")
    weight_grams = data.get("weight_grams")
    texture = data.get("texture")
    color_style = data.get("color_style")
    discontinued = data.get("discontinued")

    yarn = Yarn.query.get(id)
    if brand != None:
        yarn.brand = brand
    if name != None:
        yarn.name = name
    if weight_name != None:
        yarn.weight_name = weight_name
    if gauge != None:
        yarn.gauge = gauge
    if yardage != None:
        yarn.yardage = yardage
    if weight_grams != None:
        yarn.weight_grams = weight_grams
    if texture != None:
        yarn.texture = texture
    if color_style != None:
        yarn.color_style = color_style
    if discontinued != None:
        yarn.discontinued = discontinued

    db.session.commit()
    return jsonify(one_yarn_schema.dump(yarn))


# DELETE endpoints


@bp.route("/delete/<id>", methods=["DELETE"])
def delete_yarn_by_id(id):
    db.session.delete(Yarn.query.get(id))
    db.session.commit()
    return "Yarn deleted"


# utils


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
    if Yarn.query.get(yarn.id) is None:
        db.session.add(yarn)
    db.session.commit()


def populate_fibers(yarn, form):
    fibers = {}
    for fiber in form.fiber_type_list.entries:
        if fiber.fiber_type.data != "" and fiber.fiber_type.data is not None:
            fibers[fiber.fiber_type.data] = fiber.fiber_qty.data
    if len(fibers) > 0:
        if sum(fibers.values()) > 100:
            if current_app.config.get("TESTING"):
                print("Fiber total > 100%")
            else:
                flash("Fiber total > 100%")
        else:
            for fiber_type, fiber_amount in fibers.items():
                yarn.add_fibers(fiber_type, fiber_amount)
    else:
        flash("The entered yarn has no fiber content.")
