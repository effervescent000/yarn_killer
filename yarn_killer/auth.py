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


# GET endpoints


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


# POST endpoints


@bp.route("/signup", methods=["POST"])
def create_user():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if username and password:
        if not User.query.filter_by(username=username).first():
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            return (
                jsonify(
                    {
                        "user": one_user_schema.dump(new_user),
                        "access_token": create_access_token(identity=username),
                    }
                ),
                201,
            )
    return jsonify({"error": "invalid input"}), 400


@bp.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User.query.filter_by(username=username).first()
        if user:
            if user.check_password(password):
                return jsonify(
                    {
                        "user": one_user_schema.dump(user),
                        "access_token": create_access_token(identity=username),
                    }
                )
    return jsonify({"error": "invalid input"}), 400


# utils


@current_app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(username=identity).first()
