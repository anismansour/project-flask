from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from data import Listings  # saved db from file

import os
import app

Listings = Listings()
app = Flask(__name__)
# basedir is to locate the db file
basedir = os.path.abspath(os.path.dirname(__file__))

# database  will look for a file called db.sqlite on the current file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# init db
db = SQLAlchemy(app)
# init Marshmallow
ma = Marshmallow(app)

# User Model


class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(5000))
    picture = db.Column(db.String(5000))

    def __init__(self, title, description, picture):
        self.title = title
        self.description = description
        self. picture = picture

# LISTING schema


class ListingSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'picture')


# init schema
listing_schema = ListingSchema(strict=True)
listings_schema = ListingSchema(many=True, strict=True)


# create a listing  test route

@app.route('/test', methods=['POST'])
def add_listing():
    title = request.json['title']
    description = request.json['description']
    picture = request.json['picture']

    new_listing = Listing(title, description, picture)
    db.session.add(new_listing)
    db.session.commit()

    return listing_schema.jsonify(new_listing)


# @app.route('/test', methods=['GET'])
# def get_listings():
#     all_listings = Listing.query.all()
#     result = listings_schema.dump(all_listings)
#     return jsonify(result.data)


@app.route('/listings')
def listings():
    all_listings = Listing.query.all()
    result = listings_schema.dump(all_listings)
    return render_template("listings.html", listings=result.data)


# Listings = Listings()
# @app.route('/register', methods=['GET'])
# def get():
#     return jsonify({'msg': 'hello'})
@app.route('/')
def index():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/listing/<string:id>/')
def listing(id):
    return render_template("listing.html", id=id)


if __name__ == '__main__':
    app.run(debug=True)
