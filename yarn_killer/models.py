from selenium.webdriver.chrome import options
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

import requests
from bs4 import BeautifulSoup

from pandas import read_csv
import cv2 as cv
import numpy as np

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from . import db

from .utils import format_name


# color_indices = ['color_name', 'hex', 'r', 'g', 'b']
# color_csv = read_csv('colordata.csv', names=color_indices, header=None)

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
    colorways = db.relationship('Colorway', backref='yarn', lazy=True, cascade='all, delete-orphan')

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


class Colorway(db.Model):
    __tablename__ = 'colorways'
    id = db.Column(db.Integer, primary_key=True)
    yarn_id = db.Column(db.Integer, db.ForeignKey('yarn.id'))
    # name is the actual name of the colorway, ie "Lavender Field" or some shit
    name = db.Column(db.String(200), nullable=False)
    # value is the stripped down version, ie "lavender field"
    value = db.Column(db.String(200), nullable=False)
    # color is a String describing the color, ie "purple"
    color = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Colorway {self.name} of {self.yarn.brand} {self.yarn.name}>'


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
        elif self.store.name == 'Kraemer':
            price = soup.find('span', 'current-price').text.strip('$')
        
        if price is not None:
            self.current_price = float(price)
            self.price_updated = datetime.now()
            db.session.commit()
        else:
            print('OOPS NO DATA')
        

    def extract_colorways(self, recheck=False):
        color_indices = ['color_name', 'hex', 'r', 'g', 'b']
        color_csv = read_csv('colordata.csv', names=color_indices, header=None)

        def get_color(image):
            b, g, r, _ = cv.mean(image)
            
            minimum = 10000
            color_name = None
            for i in range(len(color_csv)):
                distance = abs(r - int(color_csv.loc[i, 'r'])) + abs(g - int(color_csv.loc[i, 'g'])) + abs(b - int(color_csv.loc[i, 'b']))
                if distance < minimum:
                    minimum = distance
                    color_name = color_csv.loc[i, 'color_name']
            return color_name


        soup = BeautifulSoup(requests.get(self.url).text, 'html.parser')
        color_labels = {}
        if self.store.name == 'Michaels':
            # colors = [x.text for x in soup.find_all('span', 'color_label')]
            # for x in colors:
            #     color_labels.add(format_name(x))
            colors = [x for x in soup.find_all('li', 'emptyswatch')]
            # for x in colors:
            #     color_labels[format_name(x.contents[1].contents[1]['title'])] = x.contents[1].contents[1]['src']
            for x in colors:
                title = None
                src = None
                for y in x.contents:
                    if y.name == 'a':
                        for z in y.contents:
                            if z.name == 'img':
                                title = z['title']
                                src = z['src']
                                break
                if title is not None and src is not None:
                    color_labels[format_name(title)] = src

        for color_name, image_src in color_labels.items():
            colorway = Colorway.query.filter_by(value=color_name[1]).first()
            image = np.asarray(np.bytearray(requests.get(image_src, stream=True).raw.read()), dtype='uint8')
            image_data = cv.imdecode(image, cv.IMREAD_COLOR)
            if colorway is None:
                colorway = Colorway(yarn_id=self.yarn_id, name=color_name[0], value=color_name[1], color=get_color(image_data))
                db.session.add(colorway)
                db.session.commit()
            elif recheck:
                colorway.color = get_color(image_data)
                db.session.commit()
            
