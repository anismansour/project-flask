from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from data import Listings  # saved db from file

import os
import app


# to generate the with sqlalchemy
# go to the python shell ==>   python on terminal
# >>> from app  import db   ==> will import the SQLALCHEMY
# >>>  db.create_all()    will create the db and file name db.sqlite that will have our db


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


# create a listing  test route with POSTMAN WORKING


@app.route('/test', methods=['POST'])
def add_listing():
    title = request.json['title']
    description = request.json['description']
    picture = request.json['picture']

    new_listing = Listing(title, description, picture)
    db.session.add(new_listing)
    db.session.commit()

    return listing_schema.jsonify(new_listing)


# CREATE ADD USING HTML PAGE not working

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template("add_listing.html")
    else:
        print(request.form)
        title = request.form['title']
        description = request.form['description']
        picture = request.form['image']

        new_listing = Listing(title, description, picture)
        db.session.add(new_listing)
        db.session.commit()
        # return listing_schema.jsonify(new_listing)
        return redirect("/listings")

# get all listings
@app.route('/listings', methods=['GET'])
def listings():
    all_listings = Listing.query.all()
    result = listings_schema.dump(all_listings)
    return render_template("listings.html", listings=result.data)

# get single listing
@app.route('/listing/<string:id>/', methods=['GET'])
def listing(id):
    listing = Listing.query.get(id)
    return render_template("listing.html", listing=listing)


# update a listing postman

@app.route('/listing/<string:id>', methods=['PUT'])
def update_listing(id):
    listing = Listing.query.get(id)

    title = request.json['title']
    description = request.json['description']
    picture = request.json['picture']

    listing.title = title
    listing.description = description
    listing.picture = picture

    db.session.commit()

    return listing_schema.jsonify(listing)

# delete listing POSTMAN
@app.route('/listing/<string:id>', methods=['DELETE'])
def delete_listing(id):
    listing = Listing.query.get(id)
    db.session.delete(listing)
    db.session.commit()

    return listing_schema.jsonify(listing)


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template("about.html")


if __name__ == '__main__':
    app.run(debug=True)
