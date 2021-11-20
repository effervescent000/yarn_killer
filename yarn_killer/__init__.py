import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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

    with app.app_context():
        from .models import User, Yarn, Fiber, Stash, Stock, Link, Store
        db.create_all()

        return app