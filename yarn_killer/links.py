from flask import (
    Blueprint,
    request,
    jsonify,
)


from .models import Yarn, Store, Link
from .schema import LinkSchema
from . import db

bp = Blueprint("links", __name__, url_prefix="/link")

one_link_schema = LinkSchema()
multi_link_schema = LinkSchema(many=True)

# GET endpoints


@bp.route("/", methods=["GET"])
def get_links():
    if len(request.args) > 0:
        yarn_id = request.args.get("yarn")
        store_id = request.args.get("store")

        all_results = []
        if yarn_id:
            all_results.append(Link.query.filter_by(yarn_id=yarn_id).all())
        if store_id:
            all_results.append(Link.query.filter_by(store_id=store_id).all())
        return jsonify(
            multi_link_schema.dump(list(set.intersection(*map(set, all_results))))
        )
    return jsonify(multi_link_schema.dump(Link.query.all()))


@bp.route("/<id>", methods=["GET"])
def get_link_by_id(id):
    return jsonify(one_link_schema.dump(Link.query.get(id)))


# POST endpoints


@bp.route("/", methods=["POST"])
def add_link():
    data = request.get_json()
    yarn_id = data.get("yarn_id")
    if not yarn_id:
        return jsonify({"error": "no ID included in request"}), 400
    url = data.get("url")
    if not url:
        return jsonify({"error": "no url included in request"}), 400
    store_data = data.get("store")
    if not store_data:
        return jsonify({"error": "no store included in request"}), 400

    store = Store.query.filter_by(name=store_data).first()
    if not store:
        store = Store(name=store_data)
        db.session.add(store)
        db.session.commit()

    yarn = Yarn.query.get(yarn_id)
    if yarn:
        response = yarn.add_link(url, store)
        return (
            jsonify(one_link_schema.dump(response["data"]))
            if "data" in response
            else (jsonify(response), 400)
        )
    return jsonify({"error": "invalid yarn"}), 400
