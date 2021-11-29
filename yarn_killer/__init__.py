import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
login_manager = LoginManager()
ma = Marshmallow()

def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        app.config.from_object('config.Config')
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    login_manager.init_app(app)
    ma.init_app(app)

    with app.app_context():
        # from .models import User, Yarn, Fiber, Stash, Stock, Link, Store
        # db.create_all()

        from . import index
        app.register_blueprint(index.bp)
        app.add_url_rule('/', endpoint='index')

        from . import yarn
        app.register_blueprint(yarn.bp)

        from . import auth
        app.register_blueprint(auth.bp)

        from . import colorway
        app.register_blueprint(colorway.bp)

        return app