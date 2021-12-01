import pytest

from yarn_killer import create_app, db
from yarn_killer.models import User, Yarn, Fiber, Stash, Stock, Store, Link

TEST_DATABASE_URI = 'sqlite:///test_database.sqlite'

@pytest.fixture
def app():
    settings_override = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': TEST_DATABASE_URI,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'dev',
        'WTF_CSRF_ENABLED': False,
        'WTF_CSRF_CHECK_DEFAULT': False,
        'WTF_CSRF_METHODS': [],
        'LOGIN_DISABLED': True
    }
    
    app = create_app(settings_override)

    with app.app_context():
        db.init_app(app)
        from yarn_killer.models import User, Yarn, Fiber, Stash, Stock, Link, Store
        db.create_all()
        
        populate_test_data()

        yield app

        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def populate_test_data():
    user_list = [
        User(username='Admin', role='admin'),
        User(username='super_user', role='super_user'),
        User(username='test_user')
    ]
    for x in user_list:
        x.set_password('test_password')
        db.session.add(x)
    db.session.commit()

    new_yarn = [
        Yarn(brand='Caron', name='Simply Soft', weight_name='Aran', gauge=18, yardage=315, weight_grams=170, texture="Plied (3+)", color_style="Solid"),
        Yarn(brand='Red Heart', name='Super Saver', weight_name='Aran', gauge=17, yardage=364, weight_grams=198, texture="Cabled", color_style="Solid"),
        Yarn(brand='Cascade Yarns', name='Cascade 220', weight_name='Worsted', gauge=19, yardage=220, weight_grams=100, texture="Plied (3+)", color_style="Solid"),
        Yarn(brand='Lion Brand', name="Vanna's Choice", weight_name='Aran', gauge=16, yardage=170, weight_grams=100, texture="Plied (3+)", color_style="Solid")
    ]

    for yarn in new_yarn:
        db.session.add(yarn)
    db.session.commit()

    Yarn.query.filter_by(brand='Caron', name='Simply Soft').first().add_fibers('Acrylic', 100)
    Yarn.query.filter_by(brand='Red Heart', name='Super Saver').first().add_fibers('Acrylic', 100)
    Yarn.query.filter_by(brand='Cascade Yarns', name='Cascade 220').first().add_fibers('Wool', 100)
    # leaving Vanna's Choice with no fibers for testing purposes
