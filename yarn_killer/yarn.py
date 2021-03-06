from flask import (
    Blueprint,
    request,
    jsonify,
)

from .models import Yarn, Fiber, Image, Store, Link
from .schema import YarnSchema, ImageSchema, LinkSchema
from . import db

bp = Blueprint("yarn", __name__, url_prefix="/yarn")

one_yarn_schema = YarnSchema()
multi_yarn_schema = YarnSchema(many=True)
one_image_schema = ImageSchema()
multi_image_schema = ImageSchema(many=True)
one_link_schema = LinkSchema()
multi_link_schema = LinkSchema(many=True)


# GET endpoints


@bp.route("/", methods=["GET"])
def get_yarn_list():
    if len(request.args) > 0:

        brand = request.args.get("brand")
        name = request.args.get("name")
        gauge = request.args.get("gauge", type=int)
        approx = request.args.get("approx", default=False, type=bool)
        weight_name = request.args.get("weightName")
        texture = request.args.get("texture")
        color_style = request.args.get("colorStyle")

        all_results = []
        if brand != None:
            all_results.append(Yarn.query.filter(Yarn.brand.ilike(f"%{brand}%")).all())
        if name != None:
            all_results.append(Yarn.query.filter(Yarn.name.ilike(f"%{name}%")).all())
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


@bp.route("/<id>", methods=["GET"])
def get_yarn_by_id(id):
    return jsonify(one_yarn_schema.dump(Yarn.query.get(id)))


@bp.route("/brands", methods=["GET"])
def get_brands():
    brands = []
    yarn_list = Yarn.query.all()
    for yarn in yarn_list:
        if yarn.brand not in brands:
            brands.append(yarn.brand)
    return jsonify(brands)


# POST endpoints


@bp.route("/", methods=["POST"])
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
    fibers = data.get("fibers")

    if not brand:
        return jsonify({"error": "no brand name included in request"})
    if not name:
        return jsonify({"error": "no name included in request"})

    yarn = Yarn.query.filter_by(brand=brand, name=name).first()
    if yarn == None:
        if not weight_name:
            return jsonify("error: Must include a weight band")
        if not gauge:
            return jsonify("error: Must include a gauge")

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

        if fibers != None:
            for fiber in fibers:
                new_fiber = Fiber(
                    yarn_id=yarn.id, type=fiber["type"], amount=fiber["amount"]
                )
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

    return jsonify(one_image_schema.dump(new_image))


# PUT endpoints


@bp.route("/<id>", methods=["PUT"])
def update_yarn_by_id(id):
    data = request.get_json()

    brand = data.get("brand")
    name = data.get("name")
    weight_name = data.get("weight_name")
    gauge = data.get("gauge")
    yardage = data.get("yardage")
    weight_grams = data.get("weight_grams")
    texture = data.get("texture")
    color_style = data.get("color_style")
    discontinued = data.get("discontinued")
    fibers = data.get("fibers")

    yarn = Yarn.query.get(id)
    if brand:
        yarn.brand = brand
    if name:
        yarn.name = name
    if weight_name:
        yarn.weight_name = weight_name
    if gauge:
        yarn.gauge = gauge
    if yardage:
        yarn.yardage = yardage
    if weight_grams:
        yarn.weight_grams = weight_grams
    if texture:
        yarn.texture = texture
    if color_style:
        yarn.color_style = color_style
    if discontinued != None:
        yarn.discontinued = discontinued

    old_fibers = Fiber.query.filter_by(yarn_id=id).all()
    if not fibers:
        purge_fibers(id)
    elif len(fibers) != len(old_fibers):
        purge_fibers(id)

    if len(old_fibers) == 0:
        for fiber in fibers:
            new_fiber = Fiber(
                yarn_id=yarn.id, type=fiber["type"], amount=fiber["amount"]
            )
            db.session.add(new_fiber)
            db.session.commit()

    db.session.commit()
    return jsonify(one_yarn_schema.dump(yarn))


# DELETE endpoints


@bp.route("/delete/<id>", methods=["DELETE"])
def delete_yarn_by_id(id):
    db.session.delete(Yarn.query.get(id))
    db.session.commit()
    return jsonify("Yarn deleted")


# utils


def purge_fibers(yarn_id):
    for fiber in Fiber.query.filter_by(yarn_id=yarn_id).all():
        db.session.delete(fiber)
        db.session.commit()
