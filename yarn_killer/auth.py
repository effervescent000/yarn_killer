from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    set_access_cookies,
    get_jwt,
    unset_jwt_cookies,
    jwt_required,
    current_user,
)


from .models import User
from .schema import UserSchema
from . import db, jwt

bp = Blueprint("auth", __name__, url_prefix="/auth")

one_user_schema = UserSchema()
multi_user_schema = UserSchema(many=True)


@bp.route("/", methods=["GET"])
def get_users():
    if request.args:
        username = request.args.get("username")
        role = request.args.get("role")

        all_results = []
        if username:
            all_results.append(User.query.filter_by(username=username).all())
        if role:
            all_results.append(User.query.filter_by(role=role).all())

        return jsonify(
            multi_user_schema.dump(list(set.intersection(*map(set, all_results))))
        )
    return jsonify(multi_user_schema.dump(User.query.all()))


@bp.route("/<id>", methods=["GET"])
def get_user(id):
    user = User.query.get(id)
    return jsonify(one_user_schema.dump(user)), 200 if user else 404
