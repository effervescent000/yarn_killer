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
