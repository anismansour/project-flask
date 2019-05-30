from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from passlib.hash import sha256_crypt


import os
import app

# source /Users/anismansour/lab/P4/.env/bin/activate
# source .env/bin/activate
# to generate the with sqlalchemy
# go to the python shell ==>   python on terminal
# >>> from app import db ==> will import the SQLALCHEMY
# >>>  db.create_all() will create the db and file name db.sqlite that will have our db


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
    price = db.Column(db.String(100))
    userId = db.Column(db.String(100))

    def __init__(self, title, description, picture, price, userId):
        self.title = title
        self.description = description
        self.picture = picture
        self.price = price
        self.userId = userId

# LISTING schema


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(1000))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
    # def __repr__(self):
    #     return '<User %r>' % self.username


class ListingSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'picture', 'price', 'userId')


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'email', 'password')


# init schema
listing_schema = ListingSchema(strict=True)
listings_schema = ListingSchema(many=True, strict=True)
user_schema = UserSchema(strict=True)
users_schema = UserSchema(many=True, strict=True)


# test route to see users in data base to be deleted
@app.route('/users', methods=['GET'])
def allusers():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return users_schema.jsonify(result.data)


# login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        print(user.__dict__)

        if not user or not sha256_crypt.verify(password, user.password):
            error = "User not found "
            return render_template('login.html', error=error)
        else:
            session['logged_in'] = True
            session['username'] = username
            return redirect('/profile')
    return render_template('login.html')


# user profile
@app.route('/profile')
def profile():
    # all_listings = Listing.query.all()
    user = User.query.filter_by(username=session['username']).first()
    all_listings = Listing.query.filter_by(userId=user.username)
    result = listings_schema.dump(all_listings)
    print(result)
    return render_template('profile.html', listings=result.data)


#  logout user

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# register route to add to database
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        print(request.form)
        username = request.form['username']
        email = request.form['email']

        password = sha256_crypt.encrypt(str(request.form['password']))

        new_user = User(username, email, password)
        db.session.add(new_user)
        db.session.commit()
        session['logged_in'] = True
        session['username'] = username

        return redirect('/profile')


# create a listing  test route with POSTMAN WORKING
# @app.route('/test', methods=['POST'])
# def add_listing():
#     title = request.json['title']
#     description = request.json['description']
#     picture = request.json['picture']

#     new_listing = Listing(title, description, picture)
#     db.session.add(new_listing)
#     db.session.commit()

#     return listing_schema.jsonify(new_listing)


# CREATE ADD USING HTML PAGE  working

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template("add_listing.html")
    else:
        print(request.form)
        title = request.form['title']
        description = request.form['description']
        picture = request.form['image']
        price = request.form['price']
        userId = request.form['userId']

        new_listing = Listing(title, description, picture, price, userId)
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

# get single listing from the user profile so he can delete and update his own listings
@app.route('/listingUser/<string:id>/', methods=['GET'])
def listingUser(id):
    listing = Listing.query.get(id)
    return render_template("userListing.html", listing=listing)


# #################################
# update on html

@app.route('/list/<string:id>', methods=['GET', 'POST'])
def up_listing(id):
    print(request.method, "<---this is the method")
    if request.method == 'GET':
        listing = Listing.query.get(id)
        return render_template("edit.html", listing=listing)
    else:
        listing = Listing.query.get(id)

        title = request.form['title']
        description = request.form['description']
        picture = request.form['image']

        listing.title = title
        listing.description = description
        listing.picture = picture
        print(listing, "<===== updated listing")
        db.session.commit()
        return redirect("/listings")

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
@app.route('/listing/<string:id>', methods=['POST'])
def delete_listing(id):
    listing = Listing.query.get(id)
    db.session.delete(listing)
    db.session.commit()

    # return listing_schema.jsonify(listing)
    return redirect("/profile")


@app.route('/')
def index():
    return render_template('home.html')


# @app.route('/login')
# def login():
#     return render_template("login.html")


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
