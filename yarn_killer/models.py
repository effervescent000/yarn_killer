from selenium.webdriver.chrome import options
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

import requests
from bs4 import BeautifulSoup

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from . import db


stores_table = db.Table('store_table',
    db.Column('yarn_id', db.Integer, db.ForeignKey('yarn.id'), primary_key=True),
    db.Column('store_id', db.Integer, db.ForeignKey('stores.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50))
    stash = db.relationship('Stash', backref='user', lazy=True, uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Create hashed password"""
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Yarn(db.Model):
    __tablename__ = 'yarn'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    brand = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    weight_name = db.Column(db.String(50))
    gauge = db.Column(db.Integer)
    yardage = db.Column(db.Integer)
    weight_grams = db.Column(db.Integer)
    discontinued = db.Column(db.Boolean, default=False)
    
    fibers = db.relationship('Fiber', backref='yarn', lazy=True, cascade='all, delete-orphan')
    links = db.relationship('Link', backref='yarn', lazy=True, cascade='all, delete-orphan')
    stores = db.relationship('Store', secondary=stores_table, back_populates='yarns')

    def __repr__(self):
        return f'<Yarn {self.brand} {self.name}>'

    def add_fibers(self, fiber_type, fiber_amount):
        total_fibers = 0
        for x in self.fibers:
            total_fibers += x.amount
        if total_fibers + fiber_amount <= 100:
            db.session.add(Fiber(yarn_id=self.id, type=fiber_type, amount=fiber_amount))
            db.session.commit()


class Fiber(db.Model):
    __tablename__ = 'fibers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    yarn_id = db.Column(db.Integer, db.ForeignKey('yarn.id'))
    type = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Fiber content {self.amount}% {self.type}>'


class Stash(db.Model):
    __tablename__ = 'stashes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    stock_list = db.relationship('Stock', backref='stash', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Stash {self.id} of user {self.user.name}>'


class Stock(db.Model):
    __tablename__ = 'stock'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # remaining weight in grams
    yarn_id = db.Column(db.Integer, db.ForeignKey('yarn.id'))
    weight = db.Column(db.Integer, nullable=False)
    stash_id = db.Column(db.Integer, db.ForeignKey('stashes.id'))
    # NO user_id column, only connecting it to the stash

    def __repr__(self):
        return f'<Stock {self.id}>'


class Store(db.Model):
    __tablename__ = 'stores'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    links = db.relationship('Link', backref='store', lazy=True, cascade='all, delete-orphan')
    yarns = db.relationship('Yarn', secondary=stores_table, back_populates='stores')

    def __repr__(self):
        return f'<Store {self.name}>'


class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(300), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    yarn_id = db.Column(db.Integer, db.ForeignKey('yarn.id'))
    current_price = db.Column(db.Float)
    price_updated = db.Column(db.DateTime)

    def update_price(self):
        price = None
        soup = BeautifulSoup(requests.get(self.url).text, 'html.parser')
        if self.store.name == 'Lion Brand':
            price = soup.find('span', 'Price').text.strip('$')
        elif self.store.name == 'Michaels':
            sale_price = soup.find('div', 'product-sales-price')
            if sale_price is not None:
                price = sale_price.text.strip().strip('From:').strip().strip('$')
        elif self.store.name == 'Joann':
            opts = Options()
            options.headless = True
            browser = Firefox(options=opts)
            browser.get(self.url)
            price_list = browser.find_elements_by_class_name('value')
            price_list = [x.text.strip() for x in price_list if x.text.strip() != '']
            price = price_list[0].strip('$')
            browser.close()
        elif self.store.name == 'LoveCrafts':
            price = soup.find('span', 'price').text.strip('$')
        elif self.store.name == 'WEBS':
            price = soup.find('span', 'product-prices__sell-price').text.strip().strip('$')
        
        if price is not None:
            self.current_price = float(price)
            self.price_updated = datetime.now()
            db.session.commit()
        else:
            print('OOPS NO DATA')
        
